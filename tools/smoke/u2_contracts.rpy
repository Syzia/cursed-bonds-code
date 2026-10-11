## tools/smoke/u2_contracts.rpy -- the second UI overhaul's contracts
## (docs/UI2_DESIGN.md section 9; docs/UI2_CONTRACTS.md), package U0c2.
##
##   SMOKE_TIMEOUT=600 tools/smoke.sh u2_contracts                              # with its overlay
##   SMOKE_TIMEOUT=600 SMOKE_ASSETS=/var/empty tools/smoke.sh u2_contracts      # the bare tree
##
## In every package's standard set. Not edited after wave 0: a wave package
## that fills a stub keeps the stub's name, signature, owning file and return
## shape, and this file goes on passing.
##
## So nothing here may depend on what the wave is PLANNED to add. Where a
## check needs today's state it makes it:
##   - the Courtyard is the test place. Its checks lay the sidecar ZZC_COURT
##     (today's five points and nothing else), and where they count its
##     hotspots (section B's spacing test, all of section I) every row a later
##     package registered there is taken out of HOT_SPOTS for the test and put
##     back (zzc_court, zzc_court_back);
##   - section A's four gates are read on test rows laid over an empty
##     manifest (zzc_blank), whatever rows the real pictures.json has by then;
##   - the dim table is kept and put back, never emptied (ZZC_HOLD["dim"]);
##   - a stub-only check stands aside, with a NOTE, once its stub is filled:
##     an empty TKY_LINES marks U5's screens, bath_ok() or pool_ok() the baths
##     and the pool, and a store function light_follow marks U3's light at an
##     hour that is only a tint (docs/UI2_CONTRACTS.md B7, B9, B10).
##
## It runs in two states and says which it is in ("NOTE state"):
##
##   overlay  tools/smoke/assets/u2_contracts/game/ is laid over the scratch
##            copy (the default): test pictures for the thirteen off-campus
##            names, a My Room evening picture, the main menu's and the menu
##            ground's pictures under test names, a test manifest row. The
##            checks that say "with an overlay" run here.
##   bare     no overlay (SMOKE_ASSETS=/var/empty): the tree as it ships. The
##            checks that say "without the file" run here.
## Everything else runs in both. The package's acceptance is both runs.
##
## Sections:
##   A  the manifest: art_rev, art_fresh, art_stem; the four gates (bg_variant,
##      view_fg_path, view_pose, light_for_place), each falling back as K7
##      says; WORLD_VARIANTS and its registration; rule_layout's for_rev
##   B  the sidecar readers: the keys of view_<place>.json with today's
##      behaviour as the default, faces.json before the tables, pose_ files,
##      path_keep_clear and the validator's applied points, hover-label sides
##   C  "Show names" and the held N key; SPOT_PLANNED and the points lint
##      accepts for it; the generic dim state; the faces at an exit's tile
##   D  the night's tables and night_club_bg; the three new actions and the
##      activity swim_pool, registered and closed; K16's test (no romance in
##      the baths or at the pool); "Ask them along" and a friend bound for Tokyo
##   E  the stubs and hooks of 9.3: every stub function, screen and label, the
##      `use` lines placed in screens other packages own, hint_seen, and a
##      Sunday ride that plays as it did
##   F  the pictures: the menus' own files, the five lenders' copies, the ten
##      names that always exist and the three that exist only with their file,
##      the board's job sites, the guarded stand-in people in three states
##   G  the test that settles D31: a pose kept on the person view by its
##      screen reaches no save
##   H  what wave 0 froze earlier and still holds: home, the eleven keys, the
##      door, asleep and away tables with their functions, the 114 icons
##   I  the picture is what is clicked (D60, 7.3; the second sitting): the
##      frozen names, the counting functions against the three test shapes of
##      tools/smoke/hot_shape_cases.json, the rules in lint (each broken test
##      sidecar refused by name), the gates, and the shaped Courtyard: no ring
##      and no icon, the square and the shape, the light, the layers, hidden
##      behind a person, dimmed (locked, a dim function, and shut by the night
##      on the Library's stacks), names shown, faces, hot_look.json, pickling,
##      and a save made on the shaped place view, loaded in the same run.
##      The test sidecar and the manifest row are laid in place, so this
##      section is the same in both states.
##
## It changes init data in place to test a gate (ART_PICTURES, RULE_LAYOUT,
## TIME_VARIANT) and puts every table back before the next section.
##
## It sets the focus (renpy.set_focus) to read a hover label, and section I
## rests the pointer on a shape (renpy.set_mouse_pos), so it takes the pointer
## lock:
## smoke-pointer

init 999 python:
    import builtins
    import copy
    import inspect
    import json
    import os

    ZZC_OVERLAY = renpy.loadable("images/bg/club.png")

    ## The eleven places the overhaul added (plan 4.1); every other place is
    ## one of the 24 the game had before it.
    ZZ_NEW_PLACES = ("boys_dorm", "yuji_room", "megumi_room", "senpai_room", "nobara_room", "maki_room",
                     "teachers_lounge", "teachers_dorm", "bathhouse", "sauna", "pool")
    ZZ_OLD_PLACES = builtins.tuple(l for l in LOC_ORDER if l not in ZZ_NEW_PLACES)

    class ZZCState(builtins.object):
        """What a section changed, so it can be put back. A builtins object:
        never saved, and rollback leaves it alone."""
        def __init__(self):
            self.art = None
            self.layout = None
            self.variant = None
            self.blank = False

    zzc = ZZCState()

    def zzc_hold():
        """Remember the three init tables the tests change in place."""
        zzc.art = copy.deepcopy(builtins.dict(ART_PICTURES))
        zzc.layout = copy.deepcopy(builtins.dict(RULE_LAYOUT))
        zzc.variant = copy.deepcopy(builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items()))

    def zzc_back():
        """Put them back, and forget every picture graded_bg has built."""
        art_rows()
        ART_PICTURES.clear()
        ART_PICTURES.update(copy.deepcopy(zzc.art))
        RULE_LAYOUT.clear()
        RULE_LAYOUT.update(copy.deepcopy(zzc.layout))
        TIME_VARIANT.clear()
        TIME_VARIANT.update(copy.deepcopy(zzc.variant))
        if zzc.blank:
            ART_PICTURES.clear()
        _BG_CACHE.clear()

    def zzc_blank(on):
        """Section A's gates are tested on rows laid over an EMPTY manifest
        (every picture at revision 1, as wave 0 ships), so that they read
        the same once the real pictures.json holds rows for the rooms they
        use. While it is on, zzc_back() leaves the manifest empty; turning
        it off puts the real rows back."""
        zzc.blank = bool(on)
        zzc_back()

    def zzc_art(**rows):
        """Lay manifest rows over the real ones (a row of None removes one)."""
        art_rows()
        for k, r in rows.items():
            if r is None:
                ART_PICTURES.pop(k, None)
            else:
                ART_PICTURES[k] = builtins.dict(r)
        _BG_CACHE.clear()

    ## The Courtyard as wave 0 left it: its four exits and the vending
    ## machine, each at the point it has today. Laid as the Courtyard's whole
    ## sidecar it makes the test place the same whatever the real file comes to
    ## hold (moved points, tips, shapes, a for_rev).
    ZZC_COURT = {"go_courtyard__gate": [1300, 985], "go_courtyard__school_yard": [84, 600], "go_courtyard__dorm_yard": [960, 310],
                 "go_courtyard__training_yard": [1640, 850], "spot_vend": [1600, 690]}

    def zzc_court(trim=False):
        """Lay the Courtyard's test sidecar: ZZC_COURT under "spots" and
        nothing else. trim=True also takes out of HOT_SPOTS every row of
        the Courtyard that is not one of those five (a hotspot a later
        package registered there; a harness's own zz rows stay), until
        zzc_court_back()."""
        if trim:
            if "spots" not in ZZC_HOLD:
                ZZC_HOLD["spots"] = builtins.list(HOT_SPOTS)
            HOT_SPOTS[:] = [h for h in HOT_SPOTS
                            if h["place"] != "courtyard" or h["id"] in ZZC_COURT or builtins.str(h["id"]).startswith("zz")]
        zzc_layout("hot_courtyard", builtins.dict(spots=ZZC_COURT))
        zzc_layout("view_courtyard", None)

    def zzc_court_back():
        """Put back the rows zzc_court(trim=True) took out. (The sidecar is
        put back by zzc_back.) Returns how many came back."""
        if "spots" not in ZZC_HOLD:
            return 0
        n = len(HOT_SPOTS)
        HOT_SPOTS[:] = ZZC_HOLD.pop("spots")
        return len(HOT_SPOTS) - n

    def zzc_plain(loc):
        """Lay a place's sidecar with its points alone (no shapes, no
        keep_tile, no tips, no for_rev): the place with its buttons."""
        zzc_layout("hot_" + loc, builtins.dict(spots=builtins.dict(rule_layout("hot_" + loc).get("spots") or {})))

    def zzc_layout(name, data):
        """Lay a sidecar over the real one (None: as if the file were absent)."""
        RULE_LAYOUT[name] = builtins.dict() if data is None else json.loads(json.dumps(data))

    def zzc_tree(d):
        """Every displayable under d, d included."""
        out = builtins.list()
        d.visit_all(out.append)
        return out

    def zzc_alpha(wid, screen="sb_place"):
        """The product of the alpha of every Transform round a button of the
        place view (1.0 for a plain one); None when it is not there."""
        sc = renpy.get_screen(screen)
        w = renpy.get_displayable(screen, wid) if sc is not None else None
        if w is None:
            return None
        a = 1.0
        for d in zzc_tree(sc):
            if isinstance(d, renpy.display.transform.Transform) and d is not w and w in zzc_tree(d):
                a *= float(d.alpha)
        return round(a, 2)

    def zzc_alone(loc, per="Noon"):
        """Stand in a place with nobody in it (everyone pinned off campus
        for the hour), the place view up."""
        store.companion = None
        store.here = loc
        store.period = per
        for w in ROSTER_ORDER:
            pin(w, "-")
        ARRIVAL[0] = None
        renpy.scene()
        renpy.show("bg", what=graded_bg())
        renpy.hide_screen("sb_place")
        renpy.show_screen("sb_place")
        zz_render(0.3)

    def zzc_key(down):
        """Post the names key going down or coming up, as the keyboard would."""
        import pygame_sdl2
        k = getattr(pygame_sdl2, ICON_NAMES_KEY)
        pygame_sdl2.event.post(pygame_sdl2.event.Event(pygame_sdl2.KEYDOWN if down else pygame_sdl2.KEYUP,
                                                       key=k, mod=0, unicode=("n" if down else ""), scancode=0, repeat=False))
        zz_render(0.3)

    def zzc_keymap_uses(key):
        """The config.keymap rows that bind a key ("K_n"), under any modifier."""
        out = builtins.list()
        letter = key[2:].lower()
        for name, rows in config.keymap.items():
            for b in (rows or ()):
                last = builtins.str(b).split("_")
                tail = "_".join(last[-2:]) if len(last) >= 2 and last[-2] == "K" else last[-1]
                if tail.lower() in (key.lower(), letter):
                    out.append((name, b))
        return out

    def zzc_face_count(who, screen="sb_place"):
        """How many face chips of this person a shown screen draws (a screen
        copies a Transform it is given, so they are told by what they crop)."""
        chip = face_chip(who, HOT_FACE_SIZE)
        sc = renpy.get_screen(screen)
        n = 0
        for d in (zzc_tree(sc) if sc is not None else ()):
            if (isinstance(d, renpy.display.transform.Transform) and d.crop is not None and d.crop == chip.crop
                    and builtins.str(getattr(d.child, "filename", "")).endswith("side/%s_neutral.png" % who)):
                n += 1
        return n

    def zzc_screen_params(name):
        """A screen's parameter names; None when there is no such screen."""
        sc = renpy.display.screen.get_screen_variant(name)
        if sc is None:
            return None
        p = sc.parameters
        return [] if p is None else [q.name for q in p.parameters.values()]

    def zzc_screen_optional(name):
        """The names of a screen's parameters that have a default (so the
        screen can be shown without them); None when there is no such
        screen."""
        sc = renpy.display.screen.get_screen_variant(name)
        if sc is None:
            return None
        p = sc.parameters
        return [] if p is None else [q.name for q in p.parameters.values() if q.default is not q.empty]

    def zzc_register(row, rows):
        """world_variants_register() run again, after init, with the
        manifest rows `rows` laid in place and the file of the planned row
        `row` taken as loadable whether or not it is there. An image may
        only be declared at init, so renpy.image is stood in for while it
        runs. Returns (used, declared) for that row alone: the rows the
        function says it used, and the images it would have declared.
        TIME_VARIANT, the manifest and the two functions are put back before
        it returns."""
        declared = builtins.list()
        loadable, image = renpy.loadable, renpy.image
        tv = copy.deepcopy(builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items()))
        art = copy.deepcopy(builtins.dict(ART_PICTURES))

        def zz_loadable(path, *args, **kwargs):
            return True if path == row[3] else loadable(path, *args, **kwargs)

        def zz_image(name, d):
            if d == row[3]:
                declared.append((name, d))

        used = builtins.list()
        try:
            zzc_art(**rows)
            renpy.loadable, renpy.image = zz_loadable, zz_image
            used = [r for r in world_variants_register() if builtins.tuple(r) == builtins.tuple(row)]
        finally:
            renpy.loadable, renpy.image = loadable, image
            TIME_VARIANT.clear()
            TIME_VARIANT.update(tv)
            art_rows()
            ART_PICTURES.clear()
            ART_PICTURES.update(art)
            _BG_CACHE.clear()
        return (used, declared)

    def zzc_uses(screen, target):
        """How many `use <target>` statements a screen's own source holds."""
        sc = renpy.display.screen.get_screen_variant(screen)
        n = 0
        todo = [sc.ast] if sc is not None else []
        while todo:
            node = todo.pop()
            if type(node).__name__ == "SLUse" and getattr(node, "target", None) == target:
                n += 1
            for attr in ("children", "entries"):
                for c in (getattr(node, attr, None) or ()):
                    todo.append(c[1] if isinstance(c, builtins.tuple) else c)
            for attr in ("block",):
                c = getattr(node, attr, None)
                if c is not None:
                    todo.append(c)
        return n

    def zzc_label_only_returns(name):
        """bool: a label's body is one statement, `return`."""
        if not renpy.has_label(name):
            return False
        node = renpy.game.script.lookup(name)
        body = getattr(node, "block", None) or []
        return len(body) == 1 and type(body[0]).__name__ == "Return"

    def zzc_label_params(name):
        node = renpy.game.script.lookup(name) if renpy.has_label(name) else None
        p = getattr(node, "parameters", None)
        return None if node is None else ([] if p is None else [q for q in p.parameters])

    def zzc_image(name):
        """The displayable an image name is defined as (a tuple or a string
        name); None when it is not defined."""
        key = builtins.tuple(name.split()) if isinstance(name, str) else builtins.tuple(name)
        return renpy.display.image.images.get(key)

    def zzc_files(name):
        """Every picture file the displayable behind an image name draws."""
        d = zzc_image(name)
        if d is None:
            return None
        return builtins.sorted(builtins.set(builtins.str(x.filename) for x in zzc_tree(d) if isinstance(x, renpy.display.im.Image)))

    def zzc_saved_pictures(path, screen=None):
        """How many displayables a save made NOW would hold that draw the
        picture file `path` (with screen=: how many times that screen is in
        it instead). What a save pickles of what is on screen is this
        context's scene lists; they are pickled as a save pickles them,
        read back, and every object in the copy is walked. (A path kept as
        a plain string, in a screen's scope, is not a displayable: a screen
        is built again after a load and asks for its pictures again.)"""
        data = renpy.compat.pickle.loads(renpy.compat.pickle.dumps(renpy.game.context().scene_lists))
        seen, todo, n = builtins.set(), [data], 0
        while todo:
            o = todo.pop()
            if id(o) in seen or isinstance(o, (str, bytes, int, float, bool, type(None))):
                continue
            seen.add(id(o))
            if screen is not None:
                if type(o).__name__ == "ScreenDisplayable" and screen in builtins.str(getattr(o, "screen_name", "")):
                    n += 1
            elif isinstance(o, renpy.display.displayable.Displayable) and builtins.str(getattr(o, "filename", "")) == path:
                n += 1
            if isinstance(o, builtins.dict):
                todo.extend(o.keys())
                todo.extend(o.values())
            elif isinstance(o, (builtins.list, builtins.tuple, builtins.set, builtins.frozenset)):
                todo.extend(o)
            else:
                d = getattr(o, "__dict__", None)
                if isinstance(d, builtins.dict):
                    todo.extend(d.values())
                for cls in type(o).__mro__:
                    slots = cls.__dict__.get("__slots__", ())
                    for k in ((slots,) if isinstance(slots, str) else slots):
                        if isinstance(k, str) and hasattr(o, k):
                            todo.append(getattr(o, k))
        return n

    def zzc_action(wid, screen="sb_place"):
        """(class name, value) of what a button does; plain values, so that
        no displayable is kept in a variable a save would pickle."""
        w = renpy.get_displayable(screen, wid)
        if w is None:
            return None
        a = w.action
        return (type(a).__name__, getattr(a, "value", None))

    def zzc_live(loc):
        """Where a place's own hotspots sit now (the sidecar applied): a set
        of (x, y), read straight from the registry."""
        side = rule_layout("hot_" + loc).get("spots") or {}
        out = builtins.set()
        for h in HOT_SPOTS:
            if h["place"] == loc and not h["id"].startswith("go_") and not h["id"].startswith("zz"):
                p = side.get(h["id"]) or (h["x"], h["y"])
                out.add((p[0], p[1]))
        return out

    def zz_dim_test():
        """A test dim function: the reason, or "" (ZZC_DIM[0])."""
        return ZZC_DIM[0]

    def zz_two_faces(to):
        """A test path_faces: two people inside the Boys' Dormitory."""
        return ["megumi", "yuji", "zz_nobody"] if to == "boys_dorm" else []

    def zz_four_faces(to):
        """A test path_faces that breaks its own promise: four people."""
        return ["megumi", "yuji", "nobara", "maki"] if to == "boys_dorm" else []

    ZZC_ASLEEP = "images/bg/gate.png"

    def zz_one_asleep(loc):
        """A test view_asleep: one sleeper painted into the Courtyard (a
        box of another place's picture stands in for the pose picture)."""
        return [("megumi", builtins.dict(image=ZZC_ASLEEP, box=(300, 300, 240, 200)))] if loc == "courtyard" else []

    def zzc_drawn(path, screen="sb_place"):
        """How many displayables of a shown screen draw the picture file
        `path`."""
        sc = renpy.get_screen(screen)
        return builtins.sum(1 for d in (zzc_tree(sc) if sc is not None else ()) if builtins.str(getattr(d, "filename", "")) == path)

    ZZC_DIM = builtins.list([""])

    def zzc_owner(fn, file):
        return callable(fn) and fn.__code__.co_filename.replace("\\", "/").endswith("game/" + file)

    def zzc_sig(fn):
        return builtins.str(inspect.signature(fn))

    ## --- section I (D60) ---------------------------------------------------------
    ## The Courtyard's whole test shapes: each exit's and the vending
    ## machine's, traced round its applied point. The gate's and the Training
    ## Yard's overlap on purpose (the gate's is the smaller); the garden's is
    ## not a rectangle, so its box holds a corner that is outside it; the exit
    ## to the School Courtyard keeps its button (keep_tile).
    ZZC_SHAPES = {
        "go_courtyard__dorm_yard":     [[[860, 250], [1060, 250], [1060, 420], [960, 420], [960, 340], [860, 340]]],
        "go_courtyard__training_yard": [[[1380, 790], [1760, 790], [1760, 960], [1380, 960]]],
        "go_courtyard__gate":          [[[1200, 900], [1460, 900], [1460, 1040], [1200, 1040]]],
        "spot_vend":                   [[[1540, 630], [1660, 630], [1660, 750], [1540, 750]]],
    }
    ZZC_KEEP = {"go_courtyard__school_yard": "test: this exit keeps its button",
                "gateway": "planned, not registered yet", "straw_posts": "planned, not registered yet"}
    ZZC_REAL = builtins.list([None])

    def zzc_d60(shapes=None, drop=(), keep=None, **more):
        """Lay the Courtyard's test sidecar in place: the real file's own
        keys, the whole test shapes with `shapes` laid over them and `drop`
        taken out, the keep_tile rows, and any other key."""
        side = json.loads(json.dumps(ZZC_REAL[0]))
        sh = json.loads(json.dumps(ZZC_SHAPES))
        sh.update(shapes or {})
        for k in drop:
            sh.pop(k, None)
        side["shapes"] = sh
        side["keep_tile"] = builtins.dict(ZZC_KEEP if keep is None else keep)
        side.update(more)
        zzc_layout("hot_courtyard", side)
        renpy.restart_interaction()

    def zzc_squares(loc, size=80):
        """Lay a test sidecar that shapes a whole place, as
        tools/smoke/make_shape_overlay.py does for all 35: a square of
        `size` px round the applied point of every exit and every hotspot
        registered there (two at one point share it), and the ids that are
        only planned under keep_tile. Returns the real sidecar, to put back
        with zzc_layout."""
        real = rule_layout("hot_" + loc)
        side = json.loads(json.dumps(real))
        reg = builtins.set(h["id"] for h in HOT_SPOTS if h["place"] == loc)
        k = size // 2
        side["shapes"] = builtins.dict((hid, [[[int(x) - k, int(y) - k], [int(x) + k, int(y) - k], [int(x) + k, int(y) + k], [int(x) - k, int(y) + k]]])
                                       for hid, (x, y) in hot_place_points(loc).items() if hid in reg)
        side["keep_tile"] = builtins.dict((hid, "planned, not registered yet") for hid in hot_planned(loc) if hid not in reg)
        side.pop("for_rev", None)
        zzc_layout("hot_" + loc, side)
        renpy.restart_interaction()
        return real

    ## The save of section I: 0 before it is made, 1 while it is being made,
    ## 2 once it has been loaded (a builtins list: a load leaves it alone).
    ZZC_SAVE = builtins.list([0, None])
    ZZC_RECOVER = builtins.list()

    def zzc_label_cb(name, abnormal):
        if name in ("load_recover", "return_recover"):
            ZZC_RECOVER.append(name)

    config.label_callbacks.append(zzc_label_cb)

    def zzc_scrub():
        """Nothing of the harness goes into a save: its working variables
        leave the store."""
        for k in [k for k in builtins.list(builtins.vars(store)) if k.startswith("_zz")]:
            try:
                builtins.delattr(store, k)
            except Exception:
                pass

    def zzc_where():
        """Where I am, as a save and its load must agree on it: the call
        depth, the day, the hour, the place, whether the place view is up,
        and the shape widgets on it."""
        sc = renpy.get_screen("sb_place")
        shapes = builtins.sorted(w for w in (sc.widgets if sc is not None else ()) if builtins.str(w).startswith("hotshape_"))
        return (renpy.call_stack_depth(), store.day, store.period, store.here, sc is not None, builtins.tuple(shapes))

    def zzc_unpicklable():
        """[(name, why)] for every store variable a save would hold that
        does not pickle."""
        bad = builtins.list()
        for k in builtins.sorted(renpy.python.store_dicts["store"].ever_been_changed):
            if k.startswith("_zz") or k not in builtins.vars(store):
                continue
            try:
                renpy.compat.pickle.dumps(getattr(store, k))
            except Exception as e:
                bad.append((k, repr(e)[:120]))
        return bad

    def zzc_save_load(slot):
        """Make the save `slot` where I stand and load it. It does not
        return: the load comes back on the statement that called it, with
        ZZC_SAVE[0] == 2 and ZZC_SAVE[1] what zzc_where() said before."""
        ZZC_SAVE[0] = 1
        ZZC_SAVE[1] = zzc_where()
        check(not zzc_unpicklable(), "I: every store variable the save will hold pickles", zzc_unpicklable())
        ## the rollback log still remembers the working variables: cut it
        ## short, so the save holds what a player's would
        del renpy.game.log.log[:-2]
        try:
            renpy.take_screenshot()
            renpy.save(slot)
            ok = bool(renpy.can_load(slot))
        except Exception as e:
            ok = repr(e)
        if not check(ok is True, "I: a save made on the place view of the shaped Courtyard is written", ok):
            ZZC_SAVE[0] = 3
            return
        ZZC_SAVE[0] = 2
        renpy.load(slot)

    def zzc_at(x, y, screen="sb_place"):
        """The id of the widget that would take a click at (x, y) now, as
        the engine picks it (the topmost focus area there); None when
        nothing would."""
        zz_render(0.2)
        f = renpy.display.render.focus_at_point(x, y)
        if f is None:
            return None
        sc = renpy.get_screen(screen)
        for wid, w in (sc.widgets.items() if sc is not None else ()):
            if w is f.widget:
                return wid
        return "?"

    def zzc_lights(screen="sb_place"):
        """{hotspot id: {part: strength}} for every shape light a shown
        screen draws: the alpha of the outer transform of each of its
        layers, told apart by the box they are drawn for."""
        sc = renpy.get_screen(screen)
        boxes = builtins.dict((hot_shape_box(sh), hid) for hid, sh in hot_shape_rows(store.here).items())
        out = builtins.dict()
        T = renpy.display.transform.Transform
        for d in (zzc_tree(sc) if sc is not None else ()):
            c = getattr(d, "child", None)
            if isinstance(d, T) and isinstance(c, T) and isinstance(getattr(c, "child", None), hot_ShapeLight):
                light = c.child
                part = "glow" if light.part == "wash" else ("dark" if light.width > HOT_SHAPE["line"] else "line")
                out.setdefault(boxes.get(light.box, "?"), builtins.dict())[part] = (round(float(d.alpha), 3), float(d.additive), c.blur)
        return out

    def zzc_fn_transforms(screen="sb_place"):
        """The names of the functions of every function transform a shown
        screen holds."""
        sc = renpy.get_screen(screen)
        return builtins.sorted(getattr(d.function, "__name__", "?") for d in (zzc_tree(sc) if sc is not None else ())
                               if isinstance(d, renpy.display.transform.Transform) and d.function is not None)

    def zzc_icons_under(wid, screen="sb_place"):
        """How many icons (a picture of images/icons/, or a stand-in's
        glyph) are drawn inside a widget; None when it is not there."""
        w = renpy.get_displayable(screen, wid)
        if w is None:
            return None
        n = 0
        for d in zzc_tree(w):
            if builtins.str(getattr(d, "filename", "")).startswith("images/icons/"):
                n += 1
            elif isinstance(d, renpy.text.text.Text) and d.style.name and "icon_glyph" in builtins.str(d.style.name):
                n += 1
        return n

    def zzc_label_rect():
        """(x, y, w, h) of the hover label as it was last drawn; None when
        none is up."""
        sc = renpy.get_screen("hover_label")
        for d in (zzc_tree(sc) if sc is not None else ()):
            if isinstance(d, renpy.display.layout.NearRect) and d.child is not None:
                size = getattr(d.child, "window_size", None)
                offs = getattr(d, "offsets", None)
                if size and offs:
                    return (int(offs[0][0]), int(offs[0][1]), int(size[0]), int(size[1]))
        return None

    def zzc_focus(wid, screen="sb_place"):
        """Focus a widget as the keyboard would, and draw."""
        renpy.set_focus(screen, wid)
        zz_render(0.35)

    def zzc_unfocus():
        """Nothing focused, as when the pointer leaves every button: the
        pointer is parked where the place view has none, and the focus (and
        with it the tooltip in force) is cleared as the engine clears it."""
        try:
            renpy.set_mouse_pos(960, 150)
        except Exception:
            pass
        zz_render(0.2)
        renpy.display.focus.override = None
        renpy.display.focus.clear_focus()
        renpy.restart_interaction()
        zz_render(0.3)

    def zzc_point(x, y, wid, screen="sb_place"):
        """Rest the pointer at (x, y). Returns "pointer" when the window
        took it (the tooltip in force is then the one under the pointer).
        A window that is not in front takes no pointer: then the widget the
        engine itself picks at that point (zzc_at; it must be `wid`) is
        focused as the pointer would focus it, and "focus" is returned;
        "missed" when the engine picks another."""
        try:
            renpy.set_mouse_pos(x, y)
        except Exception:
            pass
        zz_render(0.5)
        tip = GetTooltip()
        if isinstance(tip, builtins.tuple) and tip[1] == wid:
            return "pointer"
        if zzc_at(x, y, screen) != wid:
            return "missed"
        zzc_focus(wid, screen)
        return "focus"

    def zzc_pixel_diff(a, b, box):
        """How many pixels of a box differ between two screenshots of this
        run (by more than 6 in any channel), the box in the game's own
        1920 x 1080 and scaled to the pictures."""
        import pygame_sdl2
        pa = pygame_sdl2.image.load(os.path.join(zz_smoke_state.shots, a + ".png"))
        pb = pygame_sdl2.image.load(os.path.join(zz_smoke_state.shots, b + ".png"))
        if pa.get_size() != pb.get_size():
            return -1
        k = pa.get_size()[0] / float(config.screen_width)
        n = 0
        for y in range(int(box[1] * k), int((box[1] + box[3]) * k)):
            for x in range(int(box[0] * k), int((box[0] + box[2]) * k)):
                ca, cb = pa.get_at((x, y)), pb.get_at((x, y))
                if max(abs(ca[0] - cb[0]), abs(ca[1] - cb[1]), abs(ca[2] - cb[2])) > 6:
                    n += 1
        return n

    def zz_d60_faces(to):
        """A test path_faces: two people inside the garden's house and the
        school's."""
        return ["megumi", "yuji"] if to in ("dorm_yard", "school_yard") else []

    def zz_d60_locked(to):
        """A test path_locked: the Dormitory Garden is shut."""
        return "The garden gate is barred." if to == "dorm_yard" else ZZC_HOLD["path_locked"](to)

    def zz_d60_rects(loc):
        """A test view_person_rects: one person, over ZZC_HOLD["rect"]."""
        return [ZZC_HOLD["rect"]]

    def zz_d60_fg(loc, per=None):
        """A test view_fg_path: the room's foreground cut-out is ZZC_HOLD["fg"]."""
        return ZZC_HOLD["fg"]

    def zz_d60_rows(loc):
        """A test view_stage_rows: one person painted into the room, in
        the box ZZC_HOLD["pose"]."""
        b = ZZC_HOLD["pose"]
        return [builtins.dict(who="megumi", x=int(b[0] + b[2] / 2), yoff=-40, zoom=0.52, far=0,
                              pose=builtins.dict(image=ZZC_HOLD["pose_image"], box=b), rect=b)]

    ZZC_HOLD = builtins.dict()
    ZZC_PF = store.path_faces
    ## True when the tree itself (or an overlay) already shapes a place: the
    ## checks that say "as it ships no place is shaped" then stand aside.
    ZZC_SHAPED_TREE = builtins.any(hot_shapes_for(l) for l in LOC_ORDER)


## Section I: a patch of one flat colour with the Courtyard's hotspots on it,
## to see the light on white and on black.
screen zz_d60_patch(col):
    add Solid(col)
    use hot_layer("courtyard")
    use hot_layer("courtyard", front=True)


## D31's test screen: the person view as U3 would build it, with the painted
## pose kept in place (no fade) while the card is open.
screen zz_d31_keep(who):
    $ _zz_row = ([r for r in view_stage_rows(here) if r["who"] == who] or [None])[0]
    add graded_bg()
    if _zz_row is not None and _zz_row["pose"]:
        add view_pose_patch(_zz_row["pose"], here, ink=VIEW_INK_PERSON):
            pos (_zz_row["rect"][0], _zz_row["rect"][1])


label zz_smoke:

    $ settle(day=2, period="Noon", here="courtyard")
    $ note("state", "overlay (tools/smoke/assets/u2_contracts)" if ZZC_OVERLAY else "bare (no overlay)")

    ## --- A. the manifest and the four gates (5.5, K7) -------------------------------
    python:
        zzc_hold()
        check(zzc_owner(art_rev, "art_manifest.rpy") and zzc_owner(art_fresh, "art_manifest.rpy")
              and zzc_owner(art_validate, "art_manifest.rpy") and zzc_owner(art_stem, "art_manifest.rpy")
              and zzc_sig(art_rev) == "(stem)" and zzc_sig(art_fresh).startswith("(stem"),
              "A: art_rev(stem), art_fresh(stem), art_stem and art_validate live in art_manifest.rpy")
        check(art_rev("courtyard") in (1, 2, 3, 4, 5) and isinstance(art_rev("courtyard"), int)
              and art_rev("zz_no_such_picture") == 1 and art_fresh("zz_no_such_picture") is True,
              "A: a picture with no row is revision 1 and fresh")
        check(art_stem("dorm") == "your_room" and art_stem("courtyard") == "courtyard" and art_stem("zz") == "zz"
              and all(art_stem(l) == (l if l != "dorm" else "your_room") for l in LOCATIONS),
              "A: a place's picture stem is its key, and your_room for My Room (K1)")
        check(art_parent("dorm_common_evening") == "dorm_common" and art_parent("your_room_night") == "your_room"
              and art_parent("fg_dorm_common") == "dorm_common" and art_parent("fg_dorm_common_night") == "dorm_common_night"
              and art_parent("light_dorm") == "your_room" and art_parent("light_dorm_night") == "your_room_night"
              and art_parent("pose_dorm_common__nobara__evening") == "dorm_common_evening"
              and art_parent("pose_dorm__yuji") == "your_room" and art_parent("pose_senpai_room__panda__night__asleep") == "senpai_room_night"
              and art_parent("courtyard") is None and art_parent("map_campus") is None and art_parent("city_night") is None,
              "A: what a picture was made from is read from its name (hour pictures, fg_, light_, pose_)")
        if ZZC_OVERLAY:
            check(art_rev("zz_test_picture") == 3 and art_fresh("zz_test_child") is False and art_fresh("zz_test_fresh") is True
                  and art_rev("zz_test_child") == 1,
                  "A (overlay): pictures.json is read from game/layout/: a row's rev, a stale child, a fresh child",
                  builtins.dict(art_rows()))
        else:
            check(not renpy.loadable("layout/pictures.json") or isinstance(art_rows(), builtins.dict),
                  "A (bare): with no manifest, or the tree's own, the rows are a dict", builtins.sorted(art_rows()))

        check(art_validate() == [], "A: the tree's own manifest lints clean", art_validate())

        ## -- the manifest's rules, on rows laid in place (over an empty
        ## manifest from here to the end of the four gates: zzc_blank)
        zzc_blank(True)
        zzc_art(dorm_common=dict(rev=2, kind="inplace"))
        check(art_rev("dorm_common") == 2
              and art_fresh("dorm_common") is True
              and art_fresh("dorm_common_evening") is False and art_fresh("dorm_common_night") is False
              and art_fresh("fg_dorm_common") is False and art_fresh("fg_dorm_common_evening") is False
              and art_fresh("light_dorm_common") is False
              and art_fresh("pose_dorm_common__nobara__evening") is False
              and art_fresh("rooftop_evening") is True and art_fresh("fg_cafeteria") is True,
              "A: with the Common Room at revision 2 and no other row, everything made from its old picture is stale, and nothing else is")
        zzc_art(dorm_common_evening=dict(rev=2, kind="relight", of="dorm_common", of_rev=2),
                fg_dorm_common=dict(of="dorm_common", of_rev=2),
                fg_dorm_common_evening=dict(of="dorm_common_evening", of_rev=2),
                light_dorm_common=dict(of="dorm_common", of_rev=2))
        check(art_fresh("dorm_common_evening") and art_fresh("fg_dorm_common") and art_fresh("fg_dorm_common_evening")
              and art_fresh("light_dorm_common") and not art_fresh("dorm_common_night")
              and not art_fresh("pose_dorm_common__nobara__evening"),
              "A: a row that names its parent at the parent's revision is fresh again; a pose painted on the old evening picture is not")
        zzc_art(dorm_common=dict(rev=3, kind="inplace"))
        check(not art_fresh("dorm_common_evening") and not art_fresh("fg_dorm_common")
              and not art_fresh("fg_dorm_common_evening") and not art_fresh("light_dorm_common"),
              "A: when the parent moves on again, each row made for revision 2 is stale (and what was cut from a stale picture is too)")
        zzc_art(zz_bad=dict(rev=0), zz_bad2=dict(of="dorm_common"), zz_bad3=dict(kind="inplace"))
        _zz_f = art_validate()
        check(len(_zz_f) == 3 and all("zz_bad" in f for f in _zz_f) and not any("stale" in f for f in _zz_f),
              "A: art_validate reports a malformed row by name, and a stale row is not a finding", _zz_f)
        zzc_back()
        check(art_validate() == [] and art_rev("dorm_common") == 1, "A: (the test rows taken out again)", art_validate())

        ## -- gate 1: bg_variant (a stale hour picture is not used: the day picture, tinted)
        _zz_before = [(l, p, bg_variant(l, p)) for l in LOC_ORDER for p in PERIODS]
        check(bg_variant("dorm_common", "Evening") == "evening" and bg_variant("dorm_common", "Night") == "night"
              and bg_variant("rooftop", "Night") == "night" and bg_variant("dorm_common", "Noon") is None
              and bg_variant("zz", "Night") is None and bg_name("dorm_common", "Night") == "bg dorm_common night",
              "A: gate 1, today: bg_variant answers the hour's attribute where a painted hour exists")
        zzc_art(dorm_common=dict(rev=2, kind="inplace"))
        check(bg_variant("dorm_common", "Evening") is None and bg_variant("dorm_common", "Night") is None
              and bg_name("dorm_common", "Night") == "bg dorm_common"
              and isinstance(graded_bg("dorm_common", "Night"), Transform)
              and getattr(graded_bg("dorm_common", "Night"), "_light_key", None) == ("dorm_common", "Night")
              and bg_variant("rooftop", "Night") == "night",
              "A: gate 1: with the day picture replaced, its old evening and night are not used: the day picture, tinted for the hour")
        ## an hour picture that is fresh, in a room with a foreground whose cut for that hour is stale
        zzc_art(dorm_common_evening=dict(rev=2, kind="relight", of="dorm_common", of_rev=2))
        check(world_fg_room("dorm_common") and not world_fg_room("rooftop") and bg_variant("dorm_common", "Evening") is None,
              "A: gate 1: in a foreground room a fresh hour picture is not used until its own foreground cut is fresh")
        zzc_art(fg_dorm_common_evening=dict(of="dorm_common_evening", of_rev=2))
        check(bg_variant("dorm_common", "Evening") == "evening" and bg_variant("dorm_common", "Night") is None,
              "A: gate 1: with its cut remade the evening shows, and the night, still the old one, does not")
        zzc_back()
        check(_zz_before == [(l, p, bg_variant(l, p)) for l in LOC_ORDER for p in PERIODS], "A: (tables put back)")

        ## -- gate 2: view_fg_path (a stale foreground is not used)
        check(view_fg_path("dorm_common", "Noon") == "images/fg/fg_dorm_common.png"
              and view_fg_path("dorm_common", "Night") == "images/fg/fg_dorm_common_night.png"
              and view_fg_path("cafeteria", "Night") == "images/fg/fg_cafeteria.png" and view_fg_path("dorm", "Noon") is None,
              "A: gate 2, today: view_fg_path answers the cut for the hour's picture")
        _zz_slots = view_slots("dorm_common", 2)
        zzc_art(dorm_common=dict(rev=2, kind="inplace"))
        check(view_fg_path("dorm_common", "Noon") is None and view_fg_path("dorm_common", "Night") is None
              and view_fg_path("cafeteria", "Noon") == "images/fg/fg_cafeteria.png",
              "A: gate 2: with the room's picture replaced, the old cut is not laid over the new one")
        zzc_layout("view_dorm_common", None)
        check(view_slots("dorm_common", 2) == view_default_slots("dorm_common", 2),
              "A: gate 2: and a room whose table rows stand people behind that object falls back to the plain slots")
        zzc_art(fg_dorm_common=dict(of="dorm_common", of_rev=2))
        check(view_fg_path("dorm_common", "Noon") == "images/fg/fg_dorm_common.png"
              and view_fg_path("dorm_common", "Night") == "images/fg/fg_dorm_common.png"
              and view_slots("dorm_common", 2) == [builtins.tuple(r) for r in VIEW_SLOTS["dorm_common"][2]],
              "A: gate 2: recut for the new picture, the day cut is used again, at Night too (the day picture tinted, and its cut with it)")
        zzc_back()
        check(view_slots("dorm_common", 2) == _zz_slots, "A: (slots put back)")

        ## -- gate 3: view_pose (a stale pose is not used: the standing sprite)
        zzc_layout("pose_utahime_office", None)
        zzc_layout("view_utahime_office", dict(poses=dict(utahime=[100, 200, 300, 400])))
        fixture(period="Noon")
        _zz_p = view_pose("utahime", "utahime_office", "Noon")
        check(_zz_p == dict(image="images/place/pose_utahime_office__utahime.png", box=(100, 200, 300, 400)),
              "A: gate 3, today: a pose with no row is shown on the picture it was painted on (the box from view_<place>.json)", _zz_p)
        zzc_layout("pose_utahime_office", dict(poses=dict(utahime=[110, 210, 310, 410])))
        check(view_pose("utahime", "utahime_office", "Noon")["box"] == (110, 210, 310, 410)
              and view_pose_box("utahime_office", "utahime") == [110, 210, 310, 410],
              "A: view_pose reads pose_<place>.json before the poses key of view_<place>.json")
        zzc_layout("pose_utahime_office", dict(poses=dict(zz_other=[1, 2, 3, 4])))
        check(view_pose("utahime", "utahime_office", "Noon")["box"] == (100, 200, 300, 400),
              "A: a pose_ file without that person's box leaves the view_ file's box in force")
        zzc_art(utahime_office=dict(rev=2, kind="inplace"))
        check(view_pose("utahime", "utahime_office", "Noon") is None,
              "A: gate 3: with the room's picture replaced, the old pose is not shown (the standing sprite)")
        zzc_art(pose_utahime_office__utahime=dict(of="utahime_office", of_rev=2))
        check(view_pose("utahime", "utahime_office", "Noon") is not None,
              "A: gate 3: a pose installed on the revised picture (its row names revision 2) shows")
        zzc_back()

        ## -- gate 4: light_for_place (a stale light row is not used: the general row)
        ## (U3's light_follow, 6.2 row 2, changes one thing here: the light at
        ## an hour that is only a tint. Until it is in, that is the general
        ## row, and the three checks below say so; once a store function
        ## light_follow exists they ask only for a well-formed row that is
        ## neither the night picture's nor the day row unchanged.)
        _zz_follow = callable(getattr(store, "light_follow", None))
        if _zz_follow:
            note("A: gate 4", "U3's light_follow is in (wave 1): the pre-U3 value at an hour that is only a tint is not asserted")
        zzc_layout("light_classroom", None)
        _zz_day = light_for_place("classroom", "Noon")
        _zz_night = light_for_place("classroom", "Night")
        check(light_row("classroom") is None and light_row("classroom", "night") is None
              and _zz_day == INDOOR_LIGHT["Noon"]
              and (light_row_ok(_zz_night) if _zz_follow else _zz_night == INDOOR_LIGHT["Night"]),
              "A: gate 4, today: with no light_<place>.json a room takes the general row", (_zz_day, _zz_night))
        zzc_layout("light_classroom", {"": ["#f0e8d8", -0.02, 0.96, 0.5], "night": ["#c0c8f0", -0.1, 0.8, 0.4, -6, 1.3]})
        check(light_row("classroom") == ("#f0e8d8", -0.02, 0.96, 0.5) and light_row("classroom", "") == light_row("classroom")
              and light_row("classroom", "night") == ("#c0c8f0", -0.1, 0.8, 0.4, -6, 1.3)
              and isinstance(light_row("classroom"), builtins.tuple)
              and light_for_place("classroom", "Noon") == ("#f0e8d8", -0.02, 0.96, 0.5)
              and light_for_place("classroom", "Morning") == ("#f0e8d8", -0.02, 0.96, 0.5),
              "A: gate 4: a measured row wins while the day picture shows as painted (a row of four values, or six)")
        _zz_tint = (light_for_place("classroom", "Night"), light_for_place("classroom", "Evening"))
        check(all(light_row_ok(r) and builtins.tuple(r) not in (("#c0c8f0", -0.1, 0.8, 0.4, -6, 1.3), ("#f0e8d8", -0.02, 0.96, 0.5)) for r in _zz_tint)
              if _zz_follow else _zz_tint == (INDOOR_LIGHT["Night"], INDOOR_LIGHT["Evening"]),
              "A: gate 4: at an hour that is only a tint the general row stays (the night row waits for the night picture)", _zz_tint)
        zzc_art(classroom=dict(rev=2, kind="inplace"))
        check(light_row("classroom") is None and light_for_place("classroom", "Noon") == INDOOR_LIGHT["Noon"],
              "A: gate 4: with the room's picture replaced, the row measured on the old one is not used: the general row")
        zzc_art(light_classroom=dict(of="classroom", of_rev=2))
        check(light_for_place("classroom", "Noon") == ("#f0e8d8", -0.02, 0.96, 0.5),
              "A: gate 4: measured again on the new picture (its row names revision 2), it is used")
        zzc_layout("light_classroom", {"": ["f0e8d8", 0, 1, 0.5], "night": ["#c0c8f0", -0.1, 0.8]})
        check(light_row("classroom") is None and light_row("classroom", "night") is None
              and not light_row_ok(["#ffffff", 0, 1, True]) and not light_row_ok(["#ffffff", 0, 1, 0.5, 1])
              and light_row_ok(["#ffffff", 0, 1, 0.5]) and light_row_ok(("#ffffff", 0, 1, 0.5, 0, 1.0)),
              "A: a malformed light row is not used")
        zzc_back()
        ## a place with a painted hour: the measured row for that picture
        zzc_layout("light_rooftop", {"night": ["#a0b0e0", -0.1, 0.8, 0.4, 4, 1.2]})
        check(light_for_place("rooftop", "Night") == ("#a0b0e0", -0.1, 0.8, 0.4, 4, 1.2)
              and light_for_place("rooftop", "Evening") == PLACE_LIGHT[("rooftop", "evening")]
              and light_for_bg("bg rooftop night") == ("#a0b0e0", -0.1, 0.8, 0.4, 4, 1.2)
              and light_for_bg("bg rooftop evening") == PLACE_LIGHT[("rooftop", "evening")],
              "A: a painted hour takes its own measured row, by place and by image name; the hour beside it keeps the table's")
        zzc_art(rooftop=dict(rev=2, kind="inplace"))
        _zz_tint = light_for_place("rooftop", "Night")
        check(((light_row_ok(_zz_tint) and builtins.tuple(_zz_tint) != ("#a0b0e0", -0.1, 0.8, 0.4, 4, 1.2)) if _zz_follow else _zz_tint == OUTDOOR_LIGHT["Night"])
              and bg_variant("rooftop", "Night") is None,
              "A: and with the rooftop's day picture replaced the old night picture and its row both step aside", _zz_tint)
        zzc_back()
        ## light.json, and six values through the two functions a save reads with
        zzc_layout("light", {"bg alley": ["#101820", -0.2, 0.7, 0.3, 2, 1.1], "bg zz_bad": ["#101820", 0]})
        check(light_for_bg("bg alley") == ("#101820", -0.2, 0.7, 0.3, 2, 1.1) and light_for_bg("bg city") == BG_LIGHT["bg city"]
              and light_for_bg("bg zz_bad") == NEUTRAL_LIGHT and light_for_bg("bg zz_nothing") == NEUTRAL_LIGHT,
              "A: light.json's row for a story picture comes before BG_LIGHT; a malformed row is skipped")
        zzc_back()
        check(zzc_sig(light_for_place) == "(loc, per)" and zzc_sig(light_for_bg) == "(name)" and zzc_sig(light_row) == "(loc, variant=None)"
              and zzc_owner(light_row, "lighting.rpy")
              and light_matrix(("#ffeedd", -0.05, 0.9, 0.5)) is light_matrix(["#ffeedd", -0.05, 0.9, 0.5])
              and light_matrix(("#ffeedd", -0.05, 0.9, 0.5, 3, 1.2)) is not None,
              "A: light_for_place and light_for_bg keep their signatures; light_matrix takes a row of four or six values")
        _zz_old = store.scene_light
        _zz_t = Transform("images/fx/contact_shadow.png")
        store.scene_light = ("#ffeedd", -0.05, 0.9, 0.37, 5, 1.25)
        _zz_r1 = _sprite_light(_zz_t, 0, 0)
        _zz_r2 = _shadow_light(_zz_t, 0, 0)
        check(_zz_r1 == 0.25 and _zz_r2 == 0.25 and abs(_zz_t.alpha - 0.37) < 1e-6,
              "A: a six-value scene_light lights a sprite and its shadow without error (the shadow's opacity is the fourth value)")
        store.scene_light = ("#ffeedd", -0.05, 0.9, 0.41)
        _shadow_light(_zz_t, 0, 0)
        check(abs(_zz_t.alpha - 0.41) < 1e-6 and inspect.signature(_shadow_light).parameters.keys() == inspect.signature(_sprite_light).parameters.keys()
              and zzc_sig(_shadow_light) == "(trans, st, at)",
              "A: and a four-value one, which is what an old save holds, still does (K9: same names, same signatures)")
        store.scene_light = _zz_old

        zzc_blank(False)

        ## -- WORLD_VARIANTS (3.2, 5.7)
        _zz_rows = builtins.list(WORLD_VARIANTS)
        _zz_static = builtins.dict(dorm=("Evening", "Night"), infirmary=("Night",), rooftop=("Evening", "Night"), riverside=("Evening",),
                                   dorm_common=("Evening", "Night"), girls_dorm=("Night",))
        check(len(_zz_rows) == 56 and len(builtins.set((r[0], r[1]) for r in _zz_rows)) == 56
              and all(r[0] in LOCATIONS and r[1] in ("Evening", "Night") and r[2] == r[1].lower()
                      and r[3] == "images/bg/%s_%s.png" % (art_stem(r[0]), r[2]) for r in _zz_rows)
              and len([r for r in _zz_rows if r[0] in ZZ_OLD_PLACES]) == 37 and len([r for r in _zz_rows if r[0] not in ZZ_OLD_PLACES]) == 19,
              "A: WORLD_VARIANTS holds the 56 planned hour pictures as (place, period, attribute, file): 37 on old places, 19 on new",
              len(_zz_rows))
        check(not any(r[0] == "sauna" for r in _zz_rows)
              and not any(r[1] == "Night" and r[0] in ("office", "utahime_office", "gojo_office", "pool") for r in _zz_rows)
              and ("dorm", "Evening", "evening", "images/bg/your_room_evening.png") in _zz_rows
              and all((l, p) not in builtins.set((r[0], r[1]) for r in _zz_rows) for l, ps in _zz_static.items() for p in ps
                      if not (l == "dorm" and p == "Evening")),
              "A: no row for the sauna, for a place locked at Night, or for a picture that exists today (My Room's Evening is the one static cell a row replaces)")
        _zz_have = [r for r in _zz_rows if renpy.loadable(r[3])]
        check(all(TIME_VARIANT.get(r[0], {}).get(r[1]) == r[2] and renpy.has_image(builtins.tuple(LOCATIONS[r[0]]["bg"].split()) + (r[2],), exact=True)
                  for r in _zz_have)
              and all(TIME_VARIANT.get(r[0], {}).get(r[1]) in (None, "night") and not renpy.has_image(builtins.tuple(LOCATIONS[r[0]]["bg"].split()) + (r[2],), exact=True)
                      for r in _zz_rows if r not in _zz_have),
              "A: a row whose file exists (%d) has its image and its cell; a row whose file is missing (%d) has neither" % (len(_zz_have), len(_zz_rows) - len(_zz_have)))
        if ZZC_OVERLAY:
            check(TIME_VARIANT["dorm"]["Evening"] == "evening" and TIME_VARIANT["dorm"]["Night"] == "night"
                  and bg_variant("dorm", "Evening") == "evening" and bg_name("dorm", "Evening") == "bg your_room evening"
                  and renpy.has_image(("bg", "your_room", "evening"), exact=True)
                  and graded_bg("dorm", "Evening") == "bg your_room evening",
                  "A (overlay): a My Room evening file turns the Evening cell from night to evening, and it is shown as painted")
        else:
            check(TIME_VARIANT["dorm"]["Evening"] == ("evening" if renpy.loadable("images/bg/your_room_evening.png") else "night"),
                  "A (bare): without a My Room evening file the Evening cell is the night picture, as before",
                  TIME_VARIANT["dorm"])
        ## the registration's two clauses, on one planned row whose file is taken as there
        _zz_row = ("dorm", "Evening", "evening", "images/bg/your_room_evening.png")
        _zz_tv0 = copy.deepcopy(builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items()))
        _zz_r_fresh = zzc_register(_zz_row, builtins.dict(your_room=None, your_room_evening=None))
        _zz_r_stale = zzc_register(_zz_row, builtins.dict(your_room=dict(rev=2, kind="inplace"), your_room_evening=None))
        _zz_r_again = zzc_register(_zz_row, builtins.dict(your_room=dict(rev=2, kind="inplace"),
                                                          your_room_evening=dict(rev=2, kind="relight", of="your_room", of_rev=2)))
        check(_zz_row in WORLD_VARIANTS
              and _zz_r_fresh == ([_zz_row], [("bg your_room evening", _zz_row[3])])
              and _zz_r_stale == ([], [])
              and _zz_r_again == ([_zz_row], [("bg your_room evening", _zz_row[3])])
              and _zz_tv0 == builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items()),
              "A: world_variants_register uses a row whose file is loadable and fresh, and leaves out one whose file is loadable but stale (My Room at revision 2, its evening still the old one): no image, no cell; made again for revision 2 it registers",
              (_zz_r_fresh, _zz_r_stale, _zz_r_again))
        ## the registration's own rules, on a row whose file is known to exist
        _zz_tv = copy.deepcopy(builtins.dict((k, builtins.dict(v)) for k, v in TIME_VARIANT.items()))
        check(_validate_world() == [], "A: the world's validator is clean", _validate_world())
        TIME_VARIANT.setdefault("classroom", {})["Night"] = "night"
        _zz_f = [f for f in _validate_world() if "TIME_VARIANT" in f]
        check(len(_zz_f) == 1 and "classroom" in _zz_f[0] and "bg classroom night" in _zz_f[0],
              "A: lint reports a TIME_VARIANT cell with no image", _zz_f)
        zzc_back()

        ## -- rule_layout's for_rev (3.2)
        check(zzc_sig(rule_layout) == "(name)" and zzc_owner(rule_layout, "sb_rules.rpy")
              and rule_layout("zz_no_such_file") == {} and isinstance(rule_layout("hot_courtyard"), builtins.dict),
              "A: rule_layout(name) keeps its signature; {} for a file that does not exist")
        _zz_spots = dict(spots=dict(spot_vend=[1500, 700]))
        zzc_layout("hot_courtyard", _zz_spots)
        check(rule_layout("hot_courtyard") == _zz_spots and rule_layout("hot_courtyard") is not rule_layout("hot_courtyard")
              and rule_layout_stale("hot_courtyard") == "",
              "A: a file with no for_rev is always read (each call a fresh copy)")
        zzc_art(courtyard=dict(rev=2, kind="composed"))
        check(rule_layout("hot_courtyard") == _zz_spots,
              "A: and still read when its picture moves on (a room redone in place carries no for_rev)")
        zzc_layout("hot_courtyard", dict(_zz_spots, for_rev=2))
        zzc_layout("view_courtyard", dict(slots={"1": [[800, -40, 0.5, 0]]}, for_rev=2))
        check(rule_layout("hot_courtyard")["spots"] == _zz_spots["spots"] and view_slots("courtyard", 1) == [(800, -40, 0.5, 0)]
              and rule_validate() == [] and hot_spots_for("courtyard") is not None,
              "A: a file whose for_rev is its picture's revision is read")
        zzc_art(courtyard=dict(rev=3, kind="composed"))
        _zz_f = rule_validate()
        check(rule_layout("hot_courtyard") == {} and rule_layout("view_courtyard") == {}
              and view_slots("courtyard", 1) == [builtins.tuple(r) for r in VIEW_SLOTS["courtyard"][1]]
              and [h["x"] for h in hot_spots_for("courtyard") if h["id"] == "spot_vend"] != [1500],
              "A: a file whose for_rev does not match is ignored: the code's own numbers stand in", rule_layout("hot_courtyard"))
        check(len([f for f in _zz_f if "hot_courtyard" in f]) == 1 and all("_courtyard.json" in f for f in _zz_f) and view_validate() == [] and hot_validate() == [] and path_validate() == [],
              "A: the mismatch is no finding of view_validate, hot_validate or path_validate", (view_validate(), hot_validate(), path_validate()))
        check(rule_layout_stale("hot_courtyard") != "" and "revision 3" in rule_layout_stale("hot_courtyard")
              and rule_layout_stale("view_courtyard") != "",
              "A: and it is said, with the two revisions, by the one function lint's rule reads", rule_layout_stale("hot_courtyard"))
        zzc_layout("area_school", dict(spots={}, for_rev=4))
        zzc_layout("hot_dorm", dict(spots={}, for_rev=2))
        zzc_art(area_school=dict(rev=4, kind="composed"), your_room=dict(rev=2, kind="composed"))
        check(rule_layout_stale("area_school") == "" and rule_layout_stale("hot_dorm") == ""
              and rule_layout_picture("hot_dorm") == "your_room" and rule_layout_picture("area_school") == "area_school"
              and rule_layout_picture("pose_dorm") is None and rule_layout_picture("light") is None,
              "A: for_rev is compared with the right picture: your_room for hot_dorm, area_<key> for an area's map")
        zzc_art(your_room=None)
        check(rule_layout_stale("hot_dorm") != "" and rule_layout("hot_dorm") == {},
              "A: a for_rev of 2 on a picture still at revision 1 is a mismatch too")
        zzc_back()
        check(rule_validate() == [] and zzc_owner(rule_validate, "sb_rules.rpy"),
              "A: the tree's own layout files carry no mismatched for_rev (lint's rule, rule_validate, is clean)", rule_validate())

    ## --- B. the sidecar readers (6.1, 3.1, D57) ---------------------------------------
    python:
        zzc_hold()
        ## -- the keys of view_<place>.json, each with today's behaviour as its default
        for _zz_l in LOC_ORDER:
            zzc_layout("view_" + _zz_l, None)
        check(all(view_floor(l) is None and view_floor(l, off=True) is None for l in LOC_ORDER)
              and all(view_talk(l) == (l in VIEW_FG_TALK) for l in LOC_ORDER) and view_talk("cafeteria") is True
              and all(view_cast(l, p) is None for l in LOC_ORDER for p in PERIODS)
              and all(view_slot_light(l, n, i, p) is None for l in LOC_ORDER for p in PERIODS for n in (1, 2, 3, 4) for i in range(n)),
              "B: with no view_<place>.json no place has a floor, a cast shadow or a slot light, and the foreground stays up in dialogue only in VIEW_FG_TALK's rooms")
        _zz_sq = [[100, 900], [1700, 900], [1700, 1060], [100, 1060]]
        zzc_layout("view_classroom", dict(
            floor=dict(on=[_zz_sq], off=[[[400, 950], [600, 950], [500, 1000]]]),
            scale=[900, 300, 700],
            slot_light={"": {"2": [None, ["#ffe8c0", 0.04]]}, "Evening": {"1": [["#ffd0a0", -0.02]]}, "night": {"1": [["#000000", 0.5]]}},
            cast={"": [35, 1.4, 0.3], "Evening": [70, 2.2, 0.4]},
            talk=True))
        check(view_floor("classroom") == [[(100, 900), (1700, 900), (1700, 1060), (100, 1060)]]
              and view_floor("classroom", off=True) == [[(400, 950), (600, 950), (500, 1000)]]
              and zzc_sig(view_floor).startswith("(loc") and zzc_owner(view_floor, "view_stage.rpy"),
              "B: view_floor(loc) is the sidecar's floor as a list of polygons; off=True the parts people may not stand on")
        check(view_slot_light("classroom", 2, 1, "Noon") == ("#ffe8c0", 0.04) and view_slot_light("classroom", 2, 0, "Noon") is None
              and view_slot_light("classroom", 1, 0, "Noon") is None and view_slot_light("classroom", 1, 0, "Evening") == ("#ffd0a0", -0.02)
              and view_slot_light("classroom", 1, 0, "Night") is None and view_slot_light("classroom", 2, 5, "Noon") is None,
              "B: view_slot_light reads the hour's row for that many people: the day row by day, a period's own row first, and no night row while the room has no night picture")
        check(view_cast("classroom", "Noon") == (35, 1.4, 0.3) and view_cast("classroom", "Evening") == (70, 2.2, 0.4)
              and view_cast("classroom", "Night") == (35, 1.4, 0.3) and view_talk("classroom") is True,
              "B: view_cast and view_talk read their keys (an hour with no row of its own takes the row of the picture that shows)")
        zzc_layout("view_cafeteria", dict(talk=False, floor=[_zz_sq], cast={"": [1, 2]}, slot_light={"": {"2": [["#fff", 0]]}}))
        check(view_talk("cafeteria") is False and view_floor("cafeteria") is None and view_cast("cafeteria", "Noon") is None
              and view_slot_light("cafeteria", 2, 0, "Noon") is None,
              "B: talk=false takes the foreground down in dialogue in a room of VIEW_FG_TALK; a malformed floor, cast or slot light is not used")
        zzc_layout("view_cafeteria", dict(talk="yes"))
        check(view_talk("cafeteria") is True, "B: a talk that is not true or false leaves the table's answer")
        zzc_back()

        ## -- faces.json (D57): blink faces and boxes, the tables as the fallback
        zzc_layout("faces", None)
        check(all(view_face_box(w, k) == (builtins.tuple(VIEW_FACE[w][k]) if k in VIEW_FACE[w] else None)
                  for w in VIEW_FACE for k in ("eyes", "mouth"))
              and all(view_blink_also(w) == builtins.tuple(VIEW_BLINK_ALSO.get(w, ())) for w in CAST)
              and view_blink_also("yuji") == ("happy", "sad", "serious", "surprised")
              and view_face_box("gojo", "eyes") is None and view_face_box("zz", "eyes") is None,
              "B: with no faces.json a person's boxes are VIEW_FACE's and their blink faces VIEW_BLINK_ALSO's")
        zzc_layout("faces", dict(blink_also=dict(megumi=["happy", "angry"]),
                                 eyes=dict(megumi=[300, 280, 120, 40], yuji=[330, 290, 92, 46]),
                                 mouth=dict(yuji=[352, 348, 58, 32])))
        check(view_blink_also("megumi") == ("happy", "angry") and view_blink_also("yuji") == ("happy", "sad", "serious", "surprised")
              and view_face_box("megumi", "eyes") == (300, 280, 120, 40) and view_face_box("megumi", "mouth") == builtins.tuple(VIEW_FACE["megumi"]["mouth"])
              and view_face_box("yuji", "eyes") == (330, 290, 92, 46) and view_face_box("yuji", "mouth") == (352, 348, 58, 32)
              and view_face_box("maki", "eyes") == builtins.tuple(VIEW_FACE["maki"]["eyes"]),
              "B: a test row in faces.json moves that person's boxes and names their blink faces; everyone without a row keeps the table's")
        if renpy.loadable("images/char/fx/fx_megumi_blink.png"):
            _zz_a = view_face_layers("images/char/megumi_angry.png")
            _zz_n = view_face_layers("images/char/megumi_neutral.png")
            check(len(_zz_a) == 1 and builtins.tuple(_zz_a[0].crop) == (300, 280, 120, 40) and (_zz_a[0].xpos, _zz_a[0].ypos) == (300, 280)
                  and len(_zz_n) == 2 and builtins.tuple(_zz_n[1].crop) == builtins.tuple(VIEW_FACE["megumi"]["mouth"]),
                  "B (overlay): the blink layer is cut at the test row's box, on a face the test row names; the mouth layer stays at the table's box",
                  [(l.crop, l.xpos, l.ypos) for l in _zz_a + _zz_n])
            zzc_layout("faces", None)
            _zz_a = view_face_layers("images/char/megumi_angry.png")
            _zz_n = view_face_layers("images/char/megumi_neutral.png")
            check(_zz_a == [] and len(_zz_n) == 2 and builtins.tuple(_zz_n[0].crop) == builtins.tuple(VIEW_FACE["megumi"]["eyes"]),
                  "B (overlay): with the row gone the blink is back on VIEW_BLINK_ALSO's faces and at VIEW_FACE's box")
        else:
            check(view_face_layers("images/char/megumi_angry.png") == [] or renpy.loadable("images/char/fx/fx_megumi_blink.png"),
                  "B (bare): with no blink picture a sprite takes no layer, whatever faces.json says")
        zzc_layout("faces", None)
        check(view_validate() == [], "B: view_validate is clean on the tables", view_validate())
        zzc_layout("faces", dict(blink_also=dict(megumi=["zz_face"], zz_who=["happy"], gojo=["happy"], maki="happy"),
                                 eyes=dict(yuji=[330, 290, 92, 80], toge=[1, 2, 3]), mouth=dict(yuji=[352, 348, 58, 32])))
        _zz_f = view_validate()
        check(len(_zz_f) == 6 and any("zz_face" in f for f in _zz_f) and any("zz_who" in f for f in _zz_f)
              and any("gojo" in f and "no eye box" in f for f in _zz_f) and any("maki" in f for f in _zz_f)
              and any("toge" in f for f in _zz_f) and any("yuji" in f and "below" in f for f in _zz_f),
              "B: lint refuses a faces.json row that names no sprite, nobody, a person with no eye box, a row of the wrong shape, and a mouth box that does not lie below the eyes", _zz_f)
        zzc_back()
        check(zzc_sig(view_face_layers) == "(path)" and zzc_owner(view_face_layers, "view_stage.rpy")
              and zzc_sig(view_pose) == "(who, loc, per=None)" and zzc_sig(view_slots) == "(loc, n)",
              "B: view_face_layers, view_pose and view_slots keep their signatures")

        ## -- path_keep_clear and the validator's applied points (3.1)
        check(zzc_sig(path_keep_clear) == "(loc)" and zzc_owner(path_keep_clear, "room_paths.rpy")
              and all(isinstance(path_keep_clear(l), builtins.list) and all(isinstance(p, builtins.tuple) and len(p) == 2 for p in path_keep_clear(l))
                      and builtins.set(path_keep_clear(l)) == zzc_live(l) and len(path_keep_clear(l)) == len(zzc_live(l)) for l in LOC_ORDER)
              and path_keep_clear("zz") == [] and len(path_keep_clear("courtyard")) >= 1,
              "B: path_keep_clear(loc) is a list of (x, y): the place's own hotspots where they sit now, each point once",
              [(l, path_keep_clear(l)) for l in LOC_ORDER if path_keep_clear(l)])
        check(path_validate() == [], "B: path_validate is clean", path_validate())
        ## (the Courtyard as wave 0 left it: its four exits and the machine)
        zzc_court(trim=True)
        _zz_vend = hot_place_points("courtyard")["spot_vend"]
        check(path_keep_clear("courtyard") == [builtins.tuple(ZZC_COURT["spot_vend"])] and path_validate() == [],
              "B: (the Courtyard with its own five: one point to keep clear, the vending machine's, and path_validate still clean)",
              (path_keep_clear("courtyard"), path_validate()))
        _zz_exit = [r for r in path_exits("courtyard") if r["to"] == "training_yard"][0]
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {})["go_courtyard__training_yard"] = [_zz_vend[0] + 60, _zz_vend[1] + 30]
        zzc_layout("hot_courtyard", _zz_side)
        _zz_f = path_validate()
        check(len(_zz_f) == 1 and "go_courtyard__training_yard" in _zz_f[0] and "hotspot" in _zz_f[0],
              "B: the spacing rule reads the exit's applied point: a sidecar that puts an exit 67 px from the vending machine fails, by name", _zz_f)
        _zz_side["spots"]["go_courtyard__training_yard"] = [_zz_exit["x"], _zz_exit["y"]]
        _zz_side["spots"]["spot_vend"] = [_zz_exit["x"] + 40, _zz_exit["y"] - 40]
        zzc_layout("hot_courtyard", _zz_side)
        _zz_f = path_validate()
        check(path_keep_clear("courtyard") == [(_zz_exit["x"] + 40, _zz_exit["y"] - 40)]
              and len(_zz_f) == 1 and "go_courtyard__training_yard" in _zz_f[0],
              "B: and the hotspot's applied point: a sidecar that moves the machine onto an exit fails too", _zz_f)
        ## the code's row may be wrong where the sidecar puts it right
        zzc_back()
        zzc_court(trim=True)
        _zz_rows = builtins.list(PATH_EXITS["courtyard"])
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {})["go_courtyard__training_yard"] = [_zz_exit["x"], _zz_exit["y"]]
        zzc_layout("hot_courtyard", _zz_side)
        PATH_EXITS["courtyard"] = [(to, (_zz_vend[0] + 10 if to == "training_yard" else x), (_zz_vend[1] + 10 if to == "training_yard" else y))
                                   for to, x, y in _zz_rows]
        _zz_f = path_validate()
        PATH_EXITS["courtyard"] = _zz_rows
        check(_zz_f == [], "B: a code row that would break the rule is no finding while the sidecar's point is clear (a picture carries its numbers, K2)", _zz_f)
        zzc_back()
        zzc_court_back()
        check(path_validate() == [] and "spots" not in ZZC_HOLD
              and isinstance(path_faces("boys_dorm"), builtins.list) and zzc_owner(path_faces, "room_paths.rpy") and zzc_sig(path_faces) == "(to)",
              "B: (tables put back); path_faces(to) lives in room_paths.rpy and returns a list (section E's stub table asserts its file, signature, docstring and return shape: a list of at most three of the cast; section C asserts that the stub returns nobody)")

        ## -- hover-label sides: the sidecar's tips, then the table, then where the tile is
        fixture(here="courtyard", period="Noon")
        zzc_court()
        check(icon_tip_side(("To the Main Gate", "hot_go_courtyard__gate")) == "top"
              and icon_tip_side(("x", "hot_go_courtyard__training_yard")) == "left"
              and icon_tip_side(("x", "hot_spot_vend")) == "left" and icon_tip_side(("x", "hud_map")) == "bottom"
              and icon_tip_side(("x", "tag_yuji")) == "top" and icon_tip_side(("x", "zz_unknown")) == "left"
              and icon_tip_side("plain") == "left" and icon_tip_hot("hot_go_courtyard__gate") is None,
              "B: with no tips in the sidecar every label opens on the side it opened on before")
        zzc_layout("hot_courtyard", dict(spots=dict(ZZC_COURT),
                                         tips={"go_courtyard__gate": "right", "go_courtyard__training_yard": "bottom",
                                               "spot_vend": "top", "go_courtyard__dorm_yard": "sideways"}))
        check(icon_tip_side(("x", "hot_go_courtyard__gate")) == "right" and icon_tip_side(("x", "hot_go_courtyard__training_yard")) == "bottom"
              and icon_tip_side(("x", "hot_spot_vend")) == "top" and icon_tip_side(("x", "hot_go_courtyard__dorm_yard")) == "top"
              and icon_tip_side(("x", "hot_go_courtyard__school_yard")) == "top" and icon_tip_side(("x", "hud_map")) == "bottom",
              "B: a hot_ sidecar's tips win over the table, for an exit and for a hotspot; a side that is no side is ignored")
        fixture(here="school_yard")
        check(icon_tip_side(("x", "hot_go_courtyard__gate")) == "top" and icon_tip_side(("x", "hot_go_courtyard__training_yard")) == "left",
              "B: and they are the sides of the place I stand in: another place's sidecar says nothing here")
        fixture(here="courtyard")
        zzc_back()

    scene expression graded_bg()
    show screen sb_place
    python:
        zzc_hold()
        zzc_court()
        renpy.restart_interaction()
        zz_render(0.2)
        _zz_tip = ("Vending machine\nA can of something cold.", "hot_spot_vend")
        _zz_gate = ("To the Main Gate", "hot_go_courtyard__gate")
        _zz_ids = [h["id"] for h in hot_spots_for("courtyard")]
        check("spot_vend" in _zz_ids and "go_courtyard__gate" in _zz_ids
              and icon_tip_where(_zz_tip, "left") == "left" and icon_tip_where(_zz_gate, "top") == "top"
              and icon_tip_side(_zz_tip) == "left" and icon_tip_side(_zz_gate) == "top",
              "B: on the place view, where the label fits, a tile with no side of its own opens where it did (left of a hotspot, above an exit)", _zz_ids)
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {}).update({"spot_vend": [200, 690], "go_courtyard__gate": [1300, 40]})
        zzc_layout("hot_courtyard", _zz_side)
        check(icon_tip_side(_zz_tip) == "right" and icon_tip_side(_zz_gate) == "bottom",
              "B: and from where the tile is when it does not: right of a hotspot at the left edge, below an exit at the top")
        zzc_back()
    hide screen sb_place

    ## --- C. names shown, the planned hotspots, the dim state, faces at an exit (7.3, D36) ---
    python:
        zzc_hold()
        ## -- SPOT_PLANNED and the validator
        _zz_reg = builtins.dict((h["id"], h) for h in HOT_SPOTS)
        check(isinstance(SPOT_PLANNED, builtins.tuple) and len(SPOT_PLANNED) == len(builtins.set(r[0] for r in SPOT_PLANNED))
              and all(isinstance(r, builtins.tuple) and len(r) == 3 and r[1] in LOCATIONS and r[2] in ("look", "act") for r in SPOT_PLANNED)
              and all(builtins.sum(1 for r in SPOT_PLANNED if r[0] == "bed_" + w) == 1 for w in ("yuji", "megumi", "panda", "toge", "nobara", "maki"))
              and all(("bed_" + w, world_home(w), "look") in SPOT_PLANNED for w in ("yuji", "megumi", "panda", "toge", "nobara", "maki"))
              and all((i, l, "act") in SPOT_PLANNED for i, l in (("bath_soak", "bathhouse"), ("bath_sauna", "sauna"), ("pool_swim", "pool"))),
              "C: SPOT_PLANNED is (id, place, kind) rows, each id once: %d rows (%d looks, %d actions), the six bed tags and the three bath and pool actions among them"
              % (len(SPOT_PLANNED), len([r for r in SPOT_PLANNED if r[2] == "look"]), len([r for r in SPOT_PLANNED if r[2] == "act"])))
        _zz_things = builtins.dict((l, [r[0] for r in SPOT_PLANNED if r[1] == l] + [h["id"] for h in HOT_SPOTS if h["place"] == l and not h["id"].startswith(("go_", "zz"))])
                                   for l in LOC_ORDER)
        check(all(_zz_things[l] for l in LOC_ORDER) and len(LOC_ORDER) == 35,
              "C: with the planned ids every one of the 35 places has a thing in the picture besides its exits",
              [l for l in LOC_ORDER if not _zz_things[l]])
        check(all(r[0] not in _zz_reg or (_zz_reg[r[0]]["place"], _zz_reg[r[0]]["kind"]) == (r[1], r[2]) for r in SPOT_PLANNED)
              and hot_planned("sauna") == {"bucket": ("bucket", "sauna", "look"), "bath_sauna": ("bath_sauna", "sauna", "act")}
              and len(hot_planned()) == len(SPOT_PLANNED) and zzc_owner(hot_planned, "sb_hotspots.rpy"),
              "C: a planned id that is registered already is registered in its planned place as its planned kind")
        check(hot_validate() == [], "C: hot_validate is clean", hot_validate())
        zzc_court()
        _zz_side = rule_layout("hot_courtyard")
        _zz_side.setdefault("spots", {}).update({"gateway": [900, 520], "straw_posts": [420, 760]})
        zzc_layout("hot_courtyard", _zz_side)
        check(hot_validate() == [] and path_validate() == [],
              "C: lint accepts a sidecar point for a hotspot that is planned for the place and not registered yet", hot_validate() + path_validate())
        _zz_side["spots"].update({"zz_gone": [900, 700], "gate_pond": [700, 700], "gateway": [1500, 200], "straw_posts": "here"})
        zzc_layout("hot_courtyard", _zz_side)
        _zz_f = hot_validate()
        check(len(_zz_f) == 4 and any("zz_gone" in f and "planned" in f for f in _zz_f) and any("gate_pond" in f and "planned" in f for f in _zz_f)
              and any("gateway" in f and "lane" in f for f in _zz_f) and any("straw_posts" in f and "two numbers" in f for f in _zz_f),
              "C: and refuses a stale point (an id that is neither registered nor planned for that place; one planned for another place), a planned point in a lane, and a point that is not two numbers", _zz_f)
        zzc_back()

        ## -- names shown: the setting, the held key, and what reads them
        _zz_pers = persistent.show_names
        check(persistent.show_names is False and ICON_NAMES_KEY == "K_n" and zzc_keymap_uses(ICON_NAMES_KEY) == []
              and zzc_keymap_uses("K_TAB") != [] and ICON_NAMES_HELD[0] is False and icon_names_shown() is False,
              "C: persistent.show_names defaults to False; the names key is N and is in no config.keymap list (Tab is: the skip toggle)",
              zzc_keymap_uses(ICON_NAMES_KEY))
        _zz_w0 = [icon_words_shown(n) for n in builtins.sorted(ICONS)]
        persistent.show_names = True
        check(icon_names_shown() is True and all(icon_words_shown(n) for n in ICONS) and icon_words_shown("map", "never") is False,
              "C: with the setting on, names are shown and an icon button wears its word (not where a screen says never)")
        persistent.show_names = False
        _zz_kd = store.icon_names_key_down
        store.icon_names_key_down = lambda: True
        ICON_NAMES_HELD[0] = True
        _zz_a = icon_names_shown()
        store.icon_names_key_down = lambda: False
        _zz_b = icon_names_shown()
        check(_zz_a is True and _zz_b is False and ICON_NAMES_HELD[0] is False,
              "C: while the key is held names are shown; a key that is found up again (a key-up the window never saw) stops it")
        store.icon_names_key_down = _zz_kd
        check([icon_words_shown(n) for n in builtins.sorted(ICONS)] == _zz_w0 and zzc_owner(icon_names_shown, "ui_icons.rpy")
              and zzc_owner(icon_words_shown, "ui_icons.rpy") and zzc_sig(icon_words_shown) == "(name, words=None)",
              "C: and with neither, every icon's word shows exactly when it did before")

        ## -- on the place view
        fixture(day=2)
        zzc_court()
        zzc_alone("courtyard")
        _zz_rows = hot_spots_for("courtyard")
        _zz_names = [hot_name(h) for h in _zz_rows]
        _zz_t0 = zz_texts("sb_place")
        check(len(_zz_rows) >= 5 and "Vending machine" in _zz_names and "To the Main Gate" in _zz_names and "To the Training Yard" in _zz_names
              and not any(n in _zz_t0 for n in _zz_names),
              "C: with names not shown no exit or hotspot of the Courtyard wears its name", [n for n in _zz_names if n in _zz_t0])
        _zz_btn0 = zz_buttons("sb_place")
        _zz_r0 = [zz_rect("sb_place", "hot_" + h["id"]) for h in _zz_rows]
        shot("names_off")
        persistent.show_names = True
        renpy.restart_interaction()
        _zz_t1 = zz_texts("sb_place")
        check(all(n in _zz_t1 for n in _zz_names) and zz_buttons("sb_place") == _zz_btn0
              and [zz_rect("sb_place", "hot_" + h["id"]) for h in _zz_rows] == _zz_r0,
              "C: with the setting on every exit wears where it leads and every hotspot its name; no button is added and none moves",
              [n for n in _zz_names if n not in _zz_t1])
        shot("names_on")
        persistent.show_names = False
        renpy.restart_interaction()
        zz_render(0.2)
        ## the key itself, through the screen's own key statements
        store.icon_names_key_down = lambda: True
        zzc_key(True)
        _zz_held = ICON_NAMES_HELD[0]
        _zz_t2 = zz_texts("sb_place")
        zzc_key(False)
        _zz_t3 = zz_texts("sb_place")
        store.icon_names_key_down = _zz_kd
        check(_zz_held is True and all(n in _zz_t2 for n in _zz_names) and ICON_NAMES_HELD[0] is False and not any(n in _zz_t3 for n in _zz_names),
              "C: N going down on the place view shows the names, and coming up takes them away (the key statements in hot_layer)",
              (_zz_held, ICON_NAMES_HELD[0]))
        ## a locked exit wears where it leads, not its lock's sentence
        fixture(period="Night")
        _zz_lock = [h for h in hot_spots_for("staff_yard") if h["id"] == "go_staff_yard__office"]
        check(len(_zz_lock) == 1 and path_locked("office") != "" and hot_name(_zz_lock[0]) == "To the Principal's Office"
              and _zz_lock[0]["icon"] == "lock",
              "C: a locked exit wears where it leads (its hover label still says why it is shut)")
        fixture(period="Noon")

        ## -- the dim state (HOT_DIM is kept as it is found and put back as
        ## it was: U5 names the card table's dim function in it)
        ZZC_HOLD["dim"] = builtins.dict(HOT_DIM)
        check("spot_vend" not in HOT_DIM and hot_dim_reason([h for h in _zz_rows if h["id"] == "spot_vend"][0]) == ""
              and isinstance(HOT_DIM, builtins.dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in HOT_DIM.items())
              and HOT_DIM_ALPHA == 0.45 and zzc_owner(hot_set_dim, "sb_hotspots.rpy")
              and zzc_sig(hot_set_dim) == "(hot_id, fn)",
              "C: a hotspot that names no dim function has no reason (the vending machine); HOT_DIM is {hotspot id: function name}, and hot_set_dim(hot_id, fn) is how one names it",
              builtins.dict(HOT_DIM))
        zzc_alone("courtyard")
        check(zzc_alpha("hot_spot_vend") == 1.0 and zzc_action("hot_spot_vend") == ("Return", ("act", "spot_vend")),
              "C: the vending machine, not dim: drawn at full strength, and pressing it returns its action", (zzc_alpha("hot_spot_vend"), zzc_action("hot_spot_vend")))
        _zz_rv = hot_set_dim("spot_vend", "zz_dim_test")
        check(_zz_rv is None and hot_validate() == [], "C: hot_set_dim returns None, and lint accepts a dim function that exists", hot_validate())
        renpy.restart_interaction()
        zz_render(0.2)
        check(zzc_alpha("hot_spot_vend") == 1.0 and zzc_action("hot_spot_vend") == ("Return", ("act", "spot_vend")),
              "C: a dim function that returns \"\" changes nothing")
        ZZC_DIM[0] = "Sold out till morning."
        renpy.restart_interaction()
        zz_render(0.2)
        check(zzc_alpha("hot_spot_vend") == HOT_DIM_ALPHA and zzc_action("hot_spot_vend")[0] == "NullAction"
              and hot_dim_reason([h for h in hot_spots_for("courtyard") if h["id"] == "spot_vend"][0]) == "Sold out till morning."
              and zz_rect("sb_place", "hot_spot_vend") is not None,
              "C: while it returns a reason the hotspot is drawn at the dimmed strength and pressing it does nothing; it stays where it was",
              (zzc_alpha("hot_spot_vend"), zzc_action("hot_spot_vend")))
        renpy.set_focus("sb_place", "hot_spot_vend")
        zz_render(0.3)
        _zz_tip = GetTooltip()
        check(_zz_tip == ("Sold out till morning.", "hot_spot_vend") and "Sold out till morning." in zz_texts("hover_label"),
              "C: and its hover label says the reason, under the hotspot's own key", _zz_tip)
        shot("dim")
        renpy.set_focus(None, None)
        ZZC_DIM[0] = ""
        HOT_DIM["zz_nothing"] = "zz_no_fn"
        _zz_f = hot_validate()
        check(len(_zz_f) == 2 and all("zz_nothing" in f for f in _zz_f),
              "C: lint refuses a dim function that does not exist, and one named for an unknown hotspot", _zz_f)
        HOT_DIM.clear()
        HOT_DIM.update(ZZC_HOLD["dim"])
        check(hot_validate() == [] and "spot_vend" not in HOT_DIM, "C: (the dim table put back)", hot_validate())

        ## -- an exit's tile shows the faces path_faces returns (the garden
        ## with its buttons, and nobody on campus: zzc_alone)
        zzc_plain("dorm_yard")
        zzc_alone("dorm_yard")
        _zz_exit = [h for h in hot_spots_for("dorm_yard") if h["id"] == "go_dorm_yard__boys_dorm"][0]
        check(hot_faces(_zz_exit) == path_faces("boys_dorm") == [] and len(hot_faces(_zz_exit)) <= 3
              and zzc_face_count("megumi") == 0 and zzc_face_count("yuji") == 0,
              "C: with nobody inside the house, no face is on its exit's tile (the stub's answer everywhere)")
        _zz_pf = store.path_faces
        store.path_faces = zz_two_faces
        renpy.restart_interaction()
        zz_render(0.3)
        check(hot_faces(_zz_exit) == ["megumi", "yuji"]
              and zzc_face_count("megumi") == 1 and zzc_face_count("yuji") == 1 and zzc_face_count("panda") == 0
              and hot_faces([h for h in hot_spots_for("dorm_yard") if h["id"] == "go_dorm_yard__dorm_common"][0]) == []
              and zz_rect("sb_place", "hot_go_dorm_yard__boys_dorm") is not None,
              "C: with path_faces patched to return two people, their two faces are drawn on that exit's tile and on no other (someone who is not in the cast is left out)")
        shot("exit_faces")
        ## three at most (B9), whatever path_faces hands back
        store.path_faces = zz_four_faces
        renpy.restart_interaction()
        zz_render(0.3)
        check(hot_faces(_zz_exit) == ["megumi", "yuji", "nobara"]
              and [zzc_face_count(w) for w in ("megumi", "yuji", "nobara", "maki")] == [1, 1, 1, 0],
              "C: an exit's tile shows three faces at most: with path_faces patched to return four people, hot_faces answers the first three and three are drawn",
              (hot_faces(_zz_exit), [zzc_face_count(w) for w in ("megumi", "yuji", "nobara", "maki")]))
        store.path_faces = zz_two_faces
        renpy.restart_interaction()
        zz_render(0.2)
        ## R6's worst case for the place view with everything this sitting
        ## draws on it: names shown, faces on an exit, four toasts, the banner.
        persistent.show_names = True
        zz_worst("sb_place", name="worst_place_names")
        toast_clear()
        store.path_faces = _zz_pf
        persistent.show_names = _zz_pers
        store.schedule_overrides = {}
        zzc_back()
    hide screen sb_place

    ## --- D. the night, the activities and Tokyo: hooks, and the K16 test (3.1, 7.6, D34) ---
    python:
        settle(day=2, period="Noon", here="courtyard")
        store.schedule_overrides = {}
        for _zz_w in ROSTER_ORDER:
            if _zz_w not in store.roster:
                store.roster.append(_zz_w)
        ## -- the night's tables
        check({"pool_swim", "swim_pool", "swim", "train", "lesson", "hold"} <= builtins.set(NIGHT_REST_BLOCKS) and night_validate() == [],
              "D: pool_swim and swim_pool are in NIGHT_REST_BLOCKS, and the night's validator knows both ids", night_validate())
        check(NIGHT_CARRY_LINES["nobara_room"] == NIGHT_CARRY_LINES["girls_dorm"] == NIGHT_CARRY_LINES["maki_room"]
              and NIGHT_CARRY_LINES["girls_dorm"] != NIGHT_CARRY_LINES["dorms"],
              "D: the two girls' rooms take the girls' corridor's walk-home line")
        _zz_lines = {}
        for _zz_l in ("nobara_room", "maki_room", "girls_dorm", "yuji_room", "dorm_common"):
            store.night_carried = _zz_l
            _zz_lines[_zz_l] = night_carry_line()
        store.night_carried = ""
        check(_zz_lines["nobara_room"] == _zz_lines["maki_room"] == _zz_lines["girls_dorm"] == NIGHT_CARRY_LINES["girls_dorm"]
              and _zz_lines["yuji_room"] == _zz_lines["dorm_common"] == NIGHT_CARRY_LINES["dorms"],
              "D: night_carry_line says it for a day that turned in either room (a boy's room still takes the dormitories')", _zz_lines)
        check(zzc_owner(night_club_bg, "sb_night.rpy") and zzc_sig(night_club_bg) == "(key)"
              and all(isinstance(night_club_bg(k), str)
                      and night_club_bg(k) == ("bg club" if renpy.has_image("bg club", exact=True) else night_bg(k)) for k in NIGHT_DISTRICTS)
              and all(renpy.has_image(night_club_bg(k), exact=True) for k in NIGHT_DISTRICTS),
              "D: night_club_bg(key) is an image name that exists: bg club once that picture exists, else the district's own night",
              [night_club_bg(k) for k in NIGHT_DISTRICTS])

        ## -- the three new actions: registered, closed, labels that only return
        _zz_pa = builtins.dict((a["id"], a) for a in PLACE_ACTIONS)
        check(all(i in _zz_pa for i in ("bath_soak", "bath_sauna", "pool_swim"))
              and (_zz_pa["bath_soak"]["locs"], _zz_pa["bath_soak"]["when"], _zz_pa["bath_soak"]["cost"]) == (("bathhouse",), "bath_ok", 1)
              and (_zz_pa["bath_sauna"]["locs"], _zz_pa["bath_sauna"]["when"], _zz_pa["bath_sauna"]["cost"]) == (("sauna",), "bath_ok", 1)
              and (_zz_pa["pool_swim"]["locs"], _zz_pa["pool_swim"]["when"], _zz_pa["pool_swim"]["cost"]) == (("pool",), "pool_ok", 1)
              and all(renpy.has_label(l) for l in ("sb_do_bath_soak", "sb_do_bath_sauna", "sb_do_pool_swim", "act_swim_pool"))
              and zzc_owner(bath_ok, "room_bath.rpy") and zzc_owner(pool_ok, "room_pool.rpy")
              and isinstance(bath_ok(), bool) and isinstance(pool_ok(), bool)
              and all(icon_for("act", i) == i for i in ("bath_soak", "bath_sauna", "pool_swim")),
              "D: bath_soak, bath_sauna and pool_swim are registered place actions with their labels and icons; bath_ok() and pool_ok() are bools")
        _zz_filled = bath_ok() or pool_ok()
        if not _zz_filled:
            _zz_off = [(l, p) for l in LOC_ORDER for p in PERIODS
                       if fixture(period=p) or builtins.set(a[0] for a in place_actions(l)) & {"bath_soak", "bath_sauna", "pool_swim"}]
            check(_zz_off == [], "D (the stubs): with bath_ok() and pool_ok() False, none of the three is offered in any place at any hour", _zz_off)
            fixture(period="Noon")
            _zz_b, _zz_p = store.bath_ok, store.pool_ok
            store.bath_ok = store.pool_ok = lambda: True
            check([a[0] for a in place_actions("bathhouse") if a[0].startswith(("bath_", "pool_"))] == ["bath_soak"]
                  and [a[0] for a in place_actions("sauna") if a[0].startswith(("bath_", "pool_"))] == ["bath_sauna"]
                  and [a[0] for a in place_actions("pool") if a[0].startswith(("bath_", "pool_"))] == ["pool_swim"]
                  and not [a[0] for a in place_actions("riverside") if a[0].startswith(("bath_", "pool_"))],
                  "D (the stubs): and the day the two functions answer True, each is offered in its own place and nowhere else")
            store.bath_ok, store.pool_ok = _zz_b, _zz_p
        else:
            note("D", "bath_ok() or pool_ok() is filled (wave 1): the stub-only checks are skipped")

    ## the labels only return (the stubs): nothing is spent, nothing is shown
    if not (bath_ok() or pool_ok()):
        $ _zz_before = (store.period, store.day, store.stamina, store.here, builtins.sorted(store.actions_today))
        call sb_do_bath_soak
        call sb_do_bath_sauna
        call sb_do_pool_swim
        call act_swim_pool("yuji")
        $ check(_zz_before == (store.period, store.day, store.stamina, store.here, builtins.sorted(store.actions_today)),
                "D (the stubs): the four labels only return: no hour, no stamina, no mark")

    python:
        ## -- the swim_pool row
        _zz_row, _zz_swim = ACT_BY_ID.get("swim_pool"), ACT_BY_ID["swim"]
        check(_zz_row is not None and ACTIVITIES[-1] is _zz_row
              and all(_zz_row[k] == _zz_swim[k] for k in ("kind", "min_bond", "cost", "per", "label"))
              and _zz_row["loc"] == ("pool",) and _zz_row["when"] == "pool_ok" and _zz_swim["loc"] == ("riverside",) and "when" not in _zz_swim
              and icon_for("do", "swim_pool") == "swim" and icon_for("do", "swim_pool") in ICONS,
              "D: the activity swim_pool is appended last: swim's kind, Bond 35, cost and hours, at the pool, hidden by pool_ok; it takes the swim icon; swim stays at the riverside", _zz_row)
        store.bonds = builtins.dict((w, 100) for w in CAST)
        store.spent_today = builtins.set()
        store.stamina = 100
        if not pool_ok():
            _zz_seen = [(w, l, p) for w in ROSTER_ORDER for l in LOC_ORDER for p in PERIODS
                        if fixture(period=p, here=l) or activity_state(_zz_row, w, l) != (False, None)
                        or any(a["id"] == "swim_pool" for a, ok, why in activities_for(w, l))]
            check(_zz_seen == [], "D (the stub): \"Swim together\" at the pool is offered nowhere, with nobody, at no hour, at Bond 100", _zz_seen[:5])
            _zz_p = store.pool_ok
            store.pool_ok = lambda: True
            fixture(period="Afternoon", here="pool")
            check(activity_state(_zz_row, "yuji", "pool") == (True, None) and activity_state(_zz_row, "yuji", "riverside")[0] is False
                  and activity_state(_zz_swim, "yuji", "riverside") == (True, None),
                  "D (the stub): the day pool_ok() answers True it is offered at the pool, and swim at the river as before")
            store.pool_ok = _zz_p

        ## -- K16: no romance in the baths or at the pool
        check(ACT_NO_ROMANCE == ("bathhouse", "sauna", "pool") and builtins.set(ACT_ROMANCE_KINDS) == {"romance", "confession", "intimate"}
              and builtins.set(a["kind"] for a in ACTIVITIES) == {"friend", "romance", "confession", "intimate"},
              "D: the three kinds K16 names are every kind there is besides friend")
        store.affection = builtins.dict((w, 200) for w in CAST)
        store.together = ["maki", "shoko"]
        store.schedule_overrides = {}
        store.companion = None
        fixture(day=6, period="Evening", here="bathhouse")       # a Saturday
        _zz_here = who_is_here("bathhouse")
        _zz_at = activities_for("maki", "bathhouse")
        check(weekday() == "Sat" and "maki" in _zz_here and "maki" in stage_people("bathhouse")[0]
              and not any(a["kind"] in ACT_ROMANCE_KINDS for a, ok, why in _zz_at)
              and not any(a["id"] in ("rom_close", "int_night") for a, ok, why in _zz_at)
              and any(a["id"] == "talk" and ok for a, ok, why in _zz_at)
              and not any(c.get("romance") for c in person_choices("maki", "bathhouse")),
              "D (K16): with Maki at the Bathhouse on a weekend Evening, Bond and affection high and the two of us together, neither \"Stay a while longer\" nor \"Stay the night\" is offered there (Talk is)",
              [(a["id"], ok, why) for a, ok, why in _zz_at])
        _zz_leak = []
        for _zz_l in ACT_NO_ROMANCE:
            for _zz_p in PERIODS:
                fixture(period=_zz_p, here=_zz_l)
                for _zz_w in ROSTER_ORDER:
                    for _zz_tg in (["maki", "shoko", "nobara"], []):
                        store.together = _zz_tg
                        for a in ACTIVITIES:
                            if a["kind"] in ACT_ROMANCE_KINDS and activity_state(a, _zz_w, _zz_l) != (False, None):
                                _zz_leak.append((_zz_l, _zz_p, _zz_w, a["id"]))
        ## and not by asking about another place while I stand in one of the three
        fixture(period="Evening", here="sauna")
        store.together = ["maki"]
        _zz_leak += [("from the sauna", a["id"]) for a in ACTIVITIES
                     if a["kind"] in ACT_ROMANCE_KINDS and activity_state(a, "maki", "rooftop") != (False, None)]
        check(_zz_leak == [],
              "D (K16): no romance, confession or intimate activity is offered in the Bathhouse, the Sauna or at the Pool: with anyone, at any hour, before the confession or after", _zz_leak[:6])
        store.together = ["maki", "shoko"]
        fixture(day=6, period="Night", here="maki_room")
        _zz_at = builtins.dict((a["id"], (ok, why)) for a, ok, why in activities_for("maki", "maki_room"))
        check(not world_asleep("maki") and "maki" in stage_people("maki_room")[0]
              and _zz_at.get("rom_close") == (True, None) and _zz_at.get("int_night") == (True, None),
              "D (K16): both are offered in her room on a Night she is awake (a Saturday)", _zz_at)
        fixture(day=2, period="Night", here="maki_room")
        check(world_asleep("maki") and "maki" in who_is_here("maki_room") and stage_people("maki_room") == ([], [])
              and rail_missions("maki_room") == [],
              "D (K16): and on a Night she is asleep (a Tuesday) she is not on the stage, so nothing at all is offered with her")

        ## -- 7.6: "Ask them along" and a friend bound for Tokyo
        _zz_inv = ACT_BY_ID["invite"]
        store.together = []
        store.affection = builtins.dict((w, 0) for w in CAST)
        _zz_got = {}
        for _zz_d, _zz_p in ((7, "Morning"), (7, "Noon"), (7, "Afternoon"), (7, "Evening"), (6, "Noon"), (6, "Afternoon")):
            fixture(day=_zz_d, period=_zz_p, here="cafeteria")
            for _zz_w in ("nobara", "maki", "yuji", "megumi"):
                _zz_got[(_zz_d, _zz_p, _zz_w)] = activity_state(_zz_inv, _zz_w, "cafeteria")
        check(all(_zz_got[(7, p, w)] == (False, None) for p in ("Noon", "Afternoon") for w in ("nobara", "maki", "yuji"))
              and all(_zz_got[(7, p, w)] == (True, None) for p in ("Morning", "Evening") for w in ("nobara", "maki", "yuji"))
              and all(_zz_got[(6, p, w)] == (True, None) for p in ("Noon", "Afternoon") for w in ("nobara", "maki", "yuji"))
              and all(_zz_got[(d, p, "megumi")] == (True, None) for d, p, w in _zz_got if w == "megumi"),
              "D (7.6): \"Ask them along\" is not offered with Nobara, Maki or Yuji on a Sunday at Noon or in the Afternoon; it is on Sunday Morning and Evening, on a Saturday, and always with Megumi",
              builtins.sorted((k, v) for k, v in _zz_got.items() if v != (True, None)))
        fixture(day=7, period="Noon", here="cafeteria")
        pin("nobara", "cafeteria", per="Afternoon")
        _zz_a = activity_state(_zz_inv, "nobara", "cafeteria")
        store.schedule_overrides = {}
        check(_zz_a == (True, None) and WORLD_AWAY["nobara"] == {("Sun", "Afternoon"): "harajuku"},
              "D (7.6): someone a story pin keeps on campus that afternoon can be asked along (the same test as the clock's)", _zz_a)
        settle(day=2, period="Noon", here="courtyard")
        store.bonds = builtins.dict((w, 0) for w in CAST)

    ## --- E. the stubs and hooks of 9.3 --------------------------------------------------
    python:
        settle(day=2, period="Noon", here="courtyard")
        ## -- the stub functions: where they live, how they are called, what shape they return
        _zz_stubs = [
            ("tky_here", "room_tokyo.rpy", "(key)", lambda: tky_here("harajuku"), lambda v: isinstance(v, builtins.list) and all(w in CAST for w in v)),
            ("tky_caption", "room_tokyo.rpy", "(who, key)", lambda: tky_caption("nobara", "harajuku"), lambda v: isinstance(v, str)),
            ("map_district_people", "ui_map.rpy", "(key)", lambda: map_district_people("harajuku"),
             lambda v: isinstance(v, builtins.list) and len(v) <= 3 and all(w in CAST for w in v)),
            ("view_asleep", "view_stage.rpy", "(loc)", lambda: view_asleep("senpai_room"),
             lambda v: isinstance(v, builtins.list) and all(isinstance(r, builtins.tuple) and len(r) == 2 for r in v)),
            ("cards_invitable", "room_cards.rpy", "()", lambda: cards_invitable(), lambda v: isinstance(v, builtins.list) and all(w in CAST for w in v)),
            ("hint_show", "ui_hints.rpy", "(id)", lambda: hint_show("place"), lambda v: v is None),
            ("bath_ok", "room_bath.rpy", "()", lambda: bath_ok(), lambda v: isinstance(v, bool)),
            ("pool_ok", "room_pool.rpy", "()", lambda: pool_ok(), lambda v: isinstance(v, bool)),
            ("path_faces", "room_paths.rpy", "(to)", lambda: path_faces("boys_dorm"),
             lambda v: isinstance(v, builtins.list) and len(v) <= 3 and all(w in CAST for w in v)),
            ("night_club_bg", "sb_night.rpy", "(key)", lambda: night_club_bg("shibuya"), lambda v: isinstance(v, str)),
        ]
        _zz_bad = []
        for _zz_n, _zz_file, _zz_s, _zz_call, _zz_ok in _zz_stubs:
            _zz_fn = getattr(store, _zz_n, None)
            if not callable(_zz_fn):
                _zz_bad.append((_zz_n, "not defined"))
            elif not zzc_owner(_zz_fn, _zz_file):
                _zz_bad.append((_zz_n, "lives in", _zz_fn.__code__.co_filename))
            elif zzc_sig(_zz_fn) != _zz_s:
                _zz_bad.append((_zz_n, zzc_sig(_zz_fn)))
            elif not (_zz_fn.__doc__ or "").strip():
                _zz_bad.append((_zz_n, "no docstring"))
            elif not _zz_ok(_zz_call()):
                _zz_bad.append((_zz_n, "returned", _zz_call()))
        check(not _zz_bad, "E: every stub function of 9.2 exists in its own file with its signature, a docstring and its return shape (%d)" % len(_zz_stubs), _zz_bad)
        del _zz_stubs, _zz_call, _zz_ok      # they hold lambdas, and section G saves
        check(tky_here("harajuku") == [] and tky_caption("nobara", "harajuku") == "" and map_district_people("harajuku") == []
              and view_asleep("senpai_room") == [] and cards_invitable() == [] and hint_show("zz") is None
              or (bath_ok() or pool_ok()),
              "E (the stubs): each returns nothing: an empty list, an empty string or None")
        check(isinstance(TKY_LINES, builtins.dict) and TKY_BOND == NIGHT_OUT["bond"] == 4,
              "E: TKY_LINES is a dict and TKY_BOND is the Bond a night out gives a companion")

        ## -- the stage lays what view_asleep returns on the room, before the
        ## people, and it takes no focus (6.2 row 12; B10)
        zzc_hold()
        zzc_court(trim=True)
        zzc_alone("courtyard")
        _zz_a0, _zz_b0 = zzc_drawn(ZZC_ASLEEP), zz_buttons("sb_place")
        _zz_va = store.view_asleep
        store.view_asleep = zz_one_asleep
        renpy.restart_interaction()
        zz_render(0.3)
        _zz_a1, _zz_b1 = zzc_drawn(ZZC_ASLEEP), zz_buttons("sb_place")
        _zz_free = zzc_at(420, 400)
        shot("asleep_patch")
        store.view_asleep = _zz_va
        renpy.restart_interaction()
        zz_render(0.2)
        check(renpy.loadable(ZZC_ASLEEP) and _zz_a0 == 0 and _zz_a1 == 1 and _zz_b1 == _zz_b0 and _zz_free is None
              and zzc_drawn(ZZC_ASLEEP) == 0,
              "E: screen view_stage lays each (who, patch) view_asleep returns on the room: with it patched to return one sleeper, one patch of that picture is drawn on the place view, it adds no button and takes no click, and it is gone with the patch",
              (_zz_a0, _zz_a1, _zz_b0, _zz_b1, _zz_free))
        del _zz_va
        renpy.hide_screen("sb_place")
        zzc_back()
        zzc_court_back()
        settle(day=2, period="Noon", here="courtyard")
        store.schedule_overrides = {}

        ## -- hint_seen, the six ids
        check(isinstance(store.hint_seen, (set, builtins.set)) and HINT_IDS == ("place", "names", "map", "person", "hour", "night")
              and len(builtins.set(HINT_IDS)) == 6,
              "E: hint_seen is a set (the one new saved variable), and there are six hint ids", (store.hint_seen, HINT_IDS))
        _zz_txt = open(os.path.join(smoke_env("SMOKE_ROOT", "."), "tools", "none_ok.txt"), encoding="utf-8").read()
        check("\nhint_show\thint_show(" in _zz_txt, "E: hint_show has its row in tools/none_ok.txt")

        ## -- the screens: names and parameters
        _zz_want = [("hint_layer", []), ("view_others", ["loc", "who"]), ("cards_invite_pick", []), ("hud_day_card", ["n", "weekday"]),
                    ("tky_meet", ["key"]), ("hot_layer", ["loc", "front"]), ("view_stage", ["loc"]), ("view_fg", ["loc"]),
                    ("sb_place", []), ("sb_char", ["who"]), ("sb_map", ["layer", "area"]), ("hover_label", []),
                    ("main_menu", []), ("journal", None), ("preferences", []), ("quick_menu", []), ("file_slots", ["title"]),
                    ("choice", ["items"]), ("say", ["who", "what"])]
        _zz_bad = [(n, zzc_screen_params(n), p) for n, p in _zz_want
                   if zzc_screen_params(n) is None or (p is not None and zzc_screen_params(n) != p)]
        check(not _zz_bad, "E: the new screens exist with their parameters, and the old ones keep their names and parameters", _zz_bad)
        _zz_opt = [("hud_day_card", ["n", "weekday"]), ("hot_layer", ["front"]), ("sb_map", ["layer", "area"])]
        _zz_bad = [(n, zzc_screen_optional(n), p) for n, p in _zz_opt if zzc_screen_optional(n) != p]
        check(not _zz_bad,
              "E: and the parameters that have a default keep one: hud_day_card takes no required argument (a save that holds it loads), hot_layer's front and sb_map's layer and area stay optional",
              _zz_bad)
        check(zzc_uses("sb_place", "hint_layer") == 1 and zzc_uses("sb_map", "hint_layer") == 1 and zzc_uses("sb_char", "view_others") == 1
              and zzc_uses("sb_place", "hot_layer") == 2 and zzc_uses("sb_place", "view_stage") == 1,
              "E: the hooks are in place: `use hint_layer` in sb_place and in sb_map, `use view_others` in sb_char",
              (zzc_uses("sb_place", "hint_layer"), zzc_uses("sb_map", "hint_layer"), zzc_uses("sb_char", "view_others")))

        ## -- the labels
        check(all(renpy.has_label(l) for l in ("district_harajuku", "district_shibuya", "tky_people", "sb_do_bath_soak", "sb_do_bath_sauna",
                                                "sb_do_pool_swim", "act_swim_pool"))
              and zzc_label_params("tky_people") == ["key"] and zzc_label_params("act_swim_pool") == ["who"]
              and zzc_label_params("district_harajuku") == [] and zzc_label_params("district_shibuya") == []
              and not renpy.has_label("district_shinjuku"),
              "E: the labels the loop and the frozen sb_trip call by name exist, with their parameters")
        if not (bath_ok() or pool_ok() or tky_here("harajuku")):
            check(all(zzc_label_only_returns(l) for l in ("district_harajuku", "district_shibuya", "tky_people", "sb_do_bath_soak",
                                                          "sb_do_bath_sauna", "sb_do_pool_swim", "act_swim_pool")),
                  "E (the stubs): each of the seven labels is one statement, `return`")
    ## A filled screen waits for its own input, and a harness never waits:
    ## the two are called only while they are stubs. An empty TKY_LINES is
    ## what marks them (U5 fills the table and both screens together).
    if not TKY_LINES and not (bath_ok() or pool_ok()):
        call screen tky_meet("harajuku")
        $ _zz_m = _return
        call screen cards_invite_pick
        $ check(_zz_m == ("back",) and _return == ("close",),
                "E (the stubs): tky_meet answers ('back',) and cards_invite_pick ('close',) at once: nothing can wait on a stub", (_zz_m, _return))
    else:
        $ note("E (the stubs)", "tky_meet and cards_invite_pick are filled (wave 1): the stub-only check is skipped")

    ## -- a Sunday ride to Harajuku, with the stubs, plays exactly as today
    python:
        settle(day=7, period="Noon", here="gate")
        flag("ijichi_rides")
        store.companion = None
        store.schedule_overrides = {}
        _zz_h0 = len(_history_list)
        _zz_open = district_state("harajuku")[0] and trip_ok_now()
        autoplay()
    call sb_trip("harajuku")
    python:
        autoplay(False)
        _zz_said = [h.what for h in _history_list[_zz_h0:]]
        _zz_people = [t for t in zz_layer_tags("master") if t in CAST]
        check(_zz_open and weekday() == "Sun" and store.here == "gate" and store.period == "Evening" and "harajuku" in store.districts_visited
              and _zz_people == [] and renpy.get_screen("tky_meet") is None
              and (tky_here("harajuku") != [] or len(_zz_said) == 1 + len(DISTRICTS["harajuku"]["lines"]) + 1)
              and (tky_here("harajuku") != [] or _zz_said[1:-1] == builtins.list(DISTRICTS["harajuku"]["lines"])),
              "E: a Sunday ride to Harajuku begun at Noon ends at the gate in the Evening with nobody left on screen; with the stubs it says exactly today's lines (Ijichi's, the district's, the drive back)",
              (_zz_open, store.here, store.period, len(_zz_said), _zz_people))
        settle(day=2, period="Noon", here="courtyard")

    ## --- F. the pictures (5.8, 5.10, 8.2) ------------------------------------------------
    python:
        ## -- the menus' own pictures
        check(gui.main_menu_background == ("gui/title.png" if renpy.loadable("gui/title.png") else "images/bg/gate.png")
              and gui.game_menu_background == ("gui/menu_ground.png" if renpy.loadable("gui/menu_ground.png") else "images/bg/veil.png")
              and renpy.loadable("gui/title.png") and renpy.loadable("gui/menu_ground.png")
              and bg_placeholder("gui/zz_none.png", "images/bg/gate.png") == "images/bg/gate.png",
              "F: the main menu shows gui/title.png and the menus' ground gui/menu_ground.png, each with the old picture as its fallback",
              (gui.main_menu_background, gui.game_menu_background))

        ## -- nothing lends any more
        check(STANDIN_COPIES == ("city_night", "street_morning", "town_street", "ruin_hall", "veil")
              and all(renpy.loadable("images/bg/" + standin_copy(n)) and renpy.loadable("images/bg/%s.png" % n) for n in STANDIN_COPIES)
              and standin_copy("veil") == "standin/standin_veil.png",
              "F: the five lending pictures each have their copy under images/bg/standin/")
        _zz_lenders = builtins.set("images/bg/%s.png" % n for n in STANDIN_COPIES)
        _zz_borrow = ["bg alley", "bg alley dark", "bg ridge_veil", "bg map_tokyo", "bg shibuya", "bg shinjuku", "bg harajuku",
                      "bg kawasaki", "bg yotsuka"] + ["bg " + k for k, src in STANDIN_NAMES]
        _zz_bad = [(n, zzc_files(n)) for n in _zz_borrow if zzc_files(n) is None or builtins.set(zzc_files(n)) & _zz_lenders]
        _zz_made = [n for n in _zz_borrow if zzc_files(n) and any(f.startswith("images/bg/standin/") for f in zzc_files(n))]
        check(not _zz_bad and len(_zz_made) >= 1,
              "F: no stand-in reads a lending picture's own file any more: each is made from the copy (%d of %d names are stand-ins today)"
              % (len(_zz_made), len(_zz_borrow)), _zz_bad)
        check(zzc_files("bg city") == ["images/bg/city_night.png"] and zzc_files("bg ruin") == ["images/bg/ruin_hall.png"]
              and zzc_files("bg veil") == ["images/bg/veil.png"] and zzc_files("bg town_street") == ["images/bg/town_street.png"]
              and zzc_files("bg street_morning") == ["images/bg/street_morning.png"],
              "F: and the five lenders' own names still show their own files, so each can be painted again by itself")

        ## -- the ten names that always exist
        _zz_ten = builtins.dict(STANDIN_NAMES)
        check(builtins.sorted(_zz_ten) == builtins.sorted(["mall_front", "mall_hall", "mall_atrium", "warehouse", "annexe", "site_tunnel",
                                                           "site_ward", "site_platform", "site_pool", "site_karaoke"])
              and all(renpy.has_image(("bg", k), exact=True) for k in _zz_ten) and all(v in STANDIN_COPIES for v in _zz_ten.values()),
              "F: the ten off-campus names are always defined: the mall's three, the warehouse, the annexe and the five kinds of job site")
        _zz_with = [k for k in _zz_ten if renpy.loadable("images/bg/%s.png" % k)]
        _zz_bad = [(k, zzc_files("bg " + k)) for k in _zz_ten
                   if zzc_files("bg " + k) != (["images/bg/%s.png" % k] if k in _zz_with else ["images/bg/" + standin_copy(_zz_ten[k])])]
        if ZZC_OVERLAY:
            check(not _zz_bad and len(_zz_with) == 10, "F (overlay): with its file laid by the overlay each of the ten resolves to its own file", _zz_bad)
        else:
            check(not _zz_bad, "F (bare): without its file each of the ten resolves to its stand-in, the copy of the picture its scene plays over today (%d have their own picture)"
                  % len(_zz_with), _zz_bad)
        check((_zz_ten["mall_front"], _zz_ten["mall_hall"], _zz_ten["mall_atrium"], _zz_ten["warehouse"], _zz_ten["annexe"])
              == ("city_night", "ruin_hall", "veil", "city_night", "ruin_hall"),
              "F: each stand-in is the picture that scene shows today (bg city, bg ruin, bg veil, bg city, bg ruin), so U9's swap changes nothing on screen")
        check(light_for_bg("bg mall_front") == BG_LIGHT["bg city"] == light_for_bg("bg warehouse") == light_for_bg("bg site_platform")
              and light_for_bg("bg mall_atrium") == BG_LIGHT["bg veil"] == light_for_bg("bg site_pool")
              and light_for_bg("bg mall_hall") == light_for_bg("bg ruin") == light_for_bg("bg annexe") == light_for_bg("bg site_tunnel"),
              "F: and people are lit on each as on the picture it stands in for")

        ## -- the three that exist only with their file
        _zz_three = builtins.dict(STANDIN_IF_FILE)
        check(builtins.sorted(_zz_three) == ["bg club", "bg shibuya night", "bg shinjuku night"]
              and all(renpy.has_image(n, exact=True) == bool(renpy.loadable(f)) for n, f in _zz_three.items()),
              "F: bg club, bg shibuya night and bg shinjuku night are defined exactly when their file is loadable")
        if ZZC_OVERLAY:
            check(all(renpy.has_image(n, exact=True) and zzc_files(n) == [f] for n, f in _zz_three.items())
                  and night_bg("shibuya") == "bg shibuya night" and night_bg("shinjuku") == "bg shinjuku night"
                  and night_club_bg("shibuya") == "bg club" and night_club_bg("shinjuku") == "bg club",
                  "F (overlay): with the three files laid, all three are defined; night_bg answers each district's night and night_club_bg the club")
        else:
            _zz_none = [n for n, f in _zz_three.items() if not renpy.loadable(f)]
            check(all(not renpy.has_image(n, exact=True) for n in _zz_none)
                  and ("bg shibuya night" not in _zz_none or night_bg("shibuya") == "bg shibuya")
                  and ("bg shinjuku night" not in _zz_none or night_bg("shinjuku") == "bg shinjuku")
                  and ("bg club" not in _zz_none or all(night_club_bg(k) == night_bg(k) for k in NIGHT_DISTRICTS)),
                  "F (bare): without its file each of the three is undefined (%d of 3), and night_bg and night_club_bg return the district's own picture" % len(_zz_none),
                  _zz_none)
        check(light_for_bg("bg shibuya night") in (BG_LIGHT["bg shibuya"], builtins.tuple(rule_layout("light").get("bg shibuya night") or ()))
              and light_for_bg("bg zz_none night") == NEUTRAL_LIGHT,
              "F: a district's night with no measured row of its own keeps its district's light")
        check(not renpy.has_image("bg market", exact=True),
              "F: the Black Market's ground is a file name (images/bg/market.png), not an image name")

        ## -- the board's job-to-picture column
        _zz_kinds = builtins.dict(nerima="tunnel", edogawa="tunnel", adachi="ward", kita="ward", ikebukuro="platform", shinagawa="platform",
                                  setagaya="pool", koenji="karaoke")
        check(len(BOARD_PLACES) == 8 and all(p["bg"] == "bg site_" + _zz_kinds[p["key"]] for p in BOARD_PLACES)
              and all(renpy.has_image(p["bg"], exact=True) for p in BOARD_PLACES)
              and not [f for f in _validate_board() if "image" in f],
              "F: every board job plays over its kind of site (five kinds for eight jobs), each an image that exists; the board's validator is clean",
              [(p["key"], p["bg"]) for p in BOARD_PLACES])
        check(_validate_board() == [], "F: (the board's whole validator)", _validate_board())
    scene expression BOARD_PLACE_BY_KEY["nerima"]["bg"]
    python:
        zz_render(0.2)
        check(renpy.showing("bg site_tunnel") and store.scene_light == light_for_bg("bg site_tunnel"),
              "F: a board job's site shows by its name (the Nerima tunnel: bg site_tunnel), and sets the light")
        shot("site_tunnel")

        ## -- the stand-in people (8.2), in the three states
        _zz_keys = [k for k, path, tint in STANDIN_PEOPLE]
        check(_zz_keys == ["mother", "father", "oda", "kurose", "nade"] and all(renpy.has_image(k, exact=True) for k in _zz_keys)
              and builtins.set(STANDIN_DEFINED) <= builtins.set(_zz_keys),
              "F: mother, father, oda, kurose and nade are all defined", STANDIN_DEFINED)
        _zz_bad = []
        for _zz_k, _zz_path, _zz_tint in STANDIN_PEOPLE:
            if _zz_k in STANDIN_DEFINED:
                _zz_d = zzc_image(_zz_k)
                _zz_in = getattr(_zz_d, "child", None)
                if not (isinstance(_zz_d, Transform) and _zz_d.function is _sprite_light and isinstance(_zz_in, Transform)
                        and zzc_files(_zz_k) == [_zz_path] and _zz_in.matrixcolor == TintMatrix(_zz_tint)):
                    _zz_bad.append((_zz_k, zzc_files(_zz_k)))
        check(not _zz_bad and len(STANDIN_DEFINED) >= 1,
              "F: each name the guarded block defined (%d) is the figure it was before: a campus sprite under its tint, lit by the scene" % len(STANDIN_DEFINED), _zz_bad)
        if ZZC_OVERLAY:
            check("mother" in STANDIN_DEFINED and renpy.loadable("images/char/mother_neutral.png")
                  and zzc_files("mother") == ["images/char/shoko.png"],
                  "F (overlay): state 2, her picture has landed and the generator has not been run: `mother` is still today's figure, and nothing raised")
            _zz_d = zzc_image("nade")
            check("nade" not in STANDIN_DEFINED and "images/char/nade_neutral.png" in zzc_files("nade")
                  and "images/fx/contact_shadow.png" in zzc_files("nade") and _zz_d.function is _sprite_light,
                  "F (overlay): state 3, with the generator's line as well: `nade` is the lit_sprite, with its contact shadow, and the stand-in block left the name alone",
                  zzc_files("nade"))
            check(builtins.sorted(STANDIN_DEFINED) == ["father", "kurose", "mother", "oda"], "F (overlay): the other four are defined by the block", STANDIN_DEFINED)
        else:
            check(builtins.set(STANDIN_DEFINED) == builtins.set(k for k in _zz_keys if "images/fx/contact_shadow.png" not in zzc_files(k)),
                  "F (bare): state 1, with no generated line every one of the five is the block's (%d of 5 today)" % len(STANDIN_DEFINED), STANDIN_DEFINED)
    scene bg home_living
    show mother at pos_cl
    show nade at pos_cr
    python:
        zz_render(0.3)
        check(renpy.showing("mother") and renpy.showing("nade"), "F: `show mother` and `show nade` show, whichever is installed")
        shot("standin_people")
    hide mother
    hide nade

    ## --- G. the test that settles D31: is a pose kept on the person view screen-only? ---
    python:
        ## The sections above left displayables and test functions in their
        ## working variables; a save pickles the store, so they go first.
        for _zz_k in [k for k in builtins.vars(store) if k.startswith("_zz_")]:
            builtins.delattr(store, _zz_k)
        settle(day=2, period="Noon", here="utahime_office")
        flag("utahime_arrived")
        store.schedule_overrides = {}
        store.companion = None
        for _zz_w in ROSTER_ORDER:
            pin(_zz_w, "-")
        if "utahime" not in store.roster:
            store.roster.append("utahime")
        pin("utahime", "utahime_office")
        zzc_hold()
        zzc_layout("pose_utahime_office", dict(poses=dict(utahime=[200, 300, 500, 700])))
        _zz_pose = view_pose("utahime", "utahime_office")
        _zz_path = "images/place/pose_utahime_office__utahime.png"
        check(_zz_pose is not None and _zz_pose["image"] == _zz_path and stage_people("utahime_office")[0] == ["utahime"],
              "G: (fixture) Utahime is painted into her office", _zz_pose)
    scene expression graded_bg()
    show screen zz_d31_keep("utahime")
    python:
        zz_render(0.3)
        _zz_in_tree = any(builtins.str(getattr(d, "filename", "")) == _zz_path for d in zzc_tree(renpy.get_screen("zz_d31_keep")))
        shot("d31_pose_kept")
        _zz_a = zzc_saved_pictures(_zz_path)
        _zz_a_sc = zzc_saved_pictures(_zz_path, screen="zz_d31_keep")
    hide screen zz_d31_keep
    show screen sb_char("utahime")
    python:
        zz_render(0.5)
        _zz_b = zzc_saved_pictures(_zz_path)
        _zz_b_sc = zzc_saved_pictures(_zz_path, screen="sb_char")
    hide screen sb_char
    ## the control: the same picture SHOWN as an image, which a save does hold
    show expression Image(_zz_path) as zz_d31_shown
    python:
        zz_render(0.2)
        _zz_c = zzc_saved_pictures(_zz_path)
    hide zz_d31_shown
    python:
        check(_zz_in_tree and _zz_c >= 1 and _zz_a_sc >= 1 and _zz_b_sc >= 1,
              "G: (control) the kept pose is drawn by the screen; each screen is in what a save made on it would hold; and the same picture shown as an image IS held, as a displayable",
              (_zz_in_tree, _zz_c, _zz_a_sc, _zz_b_sc))
        check(_zz_a == 0 and _zz_b == 0,
              "G: D31 is settled: a pose kept in place by the person view's screen is screen-only. A save made on it, and one made on today's person view, would hold no displayable of the pose picture (K9)", (_zz_a, _zz_b))
        note("D31", "screen-only: U3 may keep the painted person painted while their card is open (6.2 row 8), as long as the patch is added by the screen and never shown as an image")
        zzc_back()
        settle(day=2, period="Noon", here="courtyard")
        store.schedule_overrides = {}

    ## --- H. what wave 0 froze before this sitting, and still holds (9.1) --------------------
    python:
        settle(day=2, period="Noon", here="courtyard")
        ## -- home (K1)
        check("dorm" in LOCATIONS and LOCATIONS["dorm"]["bg"] == "bg your_room" and renpy.has_label("sb_do_path_dorm")
              and renpy.has_image(("bg", "your_room"), exact=True) and renpy.loadable("images/bg/your_room.png")
              and not any(hasattr(store, n) for n in ("HOME", "WORLD_HOME", "HOME_KEY")),
              "H: home is the key dorm, the image bg your_room, the label sb_do_path_dorm (K1); there is no HOME constant")
        ## -- the eleven keys
        _zz_bad = [k for k in ZZ_NEW_PLACES
                   if not (k in LOCATIONS and LOCATIONS[k]["bg"] == "bg " + k and renpy.has_image(("bg", k), exact=True)
                           and renpy.has_label("sb_do_path_" + k) and any(a["id"] == "path_" + k for a in PLACE_ACTIONS)
                           and builtins.sum(1 for a in AREAS if k in a["places"]) == 1)]
        check(not _zz_bad and len(LOC_ORDER) == len(LOCATIONS) == 35 and len(ZZ_OLD_PLACES) == 24,
              "H: the eleven new places each have their key, image, label and action, in one area; 35 places in all", _zz_bad)
        ## -- the world's tables and their functions
        _zz_people = builtins.set(CAST)
        check(isinstance(WORLD_INSIDE, (builtins.dict, dict)) and all(k in LOCATIONS and v in LOCATIONS for k, v in WORLD_INSIDE.items())
              and all(isinstance(t, builtins.tuple) for t in (WORLD_PINLESS, WORLD_ASLEEP["weekday"], WORLD_ASLEEP["weekend"]))
              and builtins.sorted(WORLD_ASLEEP) == ["weekday", "weekend"]
              and all(w in _zz_people and l in LOCATIONS for w, l in WORLD_HOMES.items())
              and all(l in LOCATIONS and isinstance(ws, builtins.tuple) and builtins.set(ws) <= _zz_people for l, ws in WORLD_DOOR_OWNERS.items())
              and WORLD_DOOR_BOND[None] == 15
              and all(w in _zz_people and all(isinstance(c, builtins.tuple) and len(c) == 2 and c[0] in WEEKDAYS and c[1] in PERIODS and d in DISTRICTS
                                              for c, d in cells.items()) for w, cells in WORLD_AWAY.items()),
              "H: the door, asleep and away tables have their frozen shapes (WORLD_INSIDE, WORLD_PINLESS, WORLD_HOMES, WORLD_DOOR_OWNERS, WORLD_DOOR_BOND, WORLD_ASLEEP, WORLD_AWAY)")
        _zz_sigs = [("world_inside", "(loc)"), ("world_pinned", "(loc)"), ("world_home", "(who)"), ("world_door_owners", "(loc)"),
                    ("world_door_bond", "(loc)"), ("world_asleep", "(who, per=None)"), ("world_home_state", "(who, per=None)"),
                    ("world_room_state", "(loc)"), ("world_away", "(who, per=None)"), ("place_access", "(loc)"), ("person_now", "(who)"),
                    ("bg_variant", "(loc, per)")]
        _zz_bad = [(n, zzc_sig(getattr(store, n))) for n, sg in _zz_sigs
                   if not (zzc_owner(getattr(store, n, None), "sb_world.rpy") and zzc_sig(getattr(store, n)) == sg)]
        check(not _zz_bad, "H: their functions live in sb_world.rpy with their signatures (%d)" % len(_zz_sigs), _zz_bad)
        check(world_inside("dorm") == "boys_dorm" and world_inside("courtyard") is None and world_pinned("dorm") and not world_pinned("yuji_room")
              and world_home("yuji") == "yuji_room" and world_home("gojo") is None
              and world_door_bond("yuji_room") == 15 and world_door_bond("courtyard") is None
              and isinstance(world_door_owners("senpai_room"), builtins.list) and builtins.sorted(world_door_owners("senpai_room")) == ["panda", "toge"]
              and world_asleep("megumi") is False and world_home_state("megumi") in ("awake", "asleep", "out")
              and isinstance(world_room_state("senpai_room"), (builtins.dict, dict)) and builtins.sorted(world_room_state("senpai_room")) == ["panda", "toge"]
              and world_room_state("courtyard") == {} and world_away("nobara") is None,
              "H: and answer in their frozen shapes (a house's key or None; a bool; a place or None; an int or None; a list; awake, asleep or out; a dict by owner; a district or None)")
        _zz_pn = person_now("yuji")
        _zz_pa = [place_access(l) for l in LOC_ORDER]
        check(builtins.sorted(_zz_pn) == ["doing", "hidden", "name", "place", "reachable", "with_me"]
              and all(isinstance(r, builtins.tuple) and len(r) == 3 and isinstance(r[0], bool) and isinstance(r[1], str) and isinstance(r[2], str) for r in _zz_pa),
              "H: person_now has exactly its six keys, and place_access answers (bool, reason, short tag) for every place")
        flag("door_megumi_room")
        store.bonds["megumi"] = 0
        fixture(here="boys_dorm")
        _zz_open = place_access("megumi_room")[0]
        store.flags.discard("door_megumi_room")
        check(_zz_open and not place_access("megumi_room")[0] and place_access("megumi_room")[2] == "Bond 15",
              "H: the flag door_<place> opens a door at Bond 0, and without it the door asks Bond 15 (the hook for later quests, D49)")
        fixture(here="courtyard")
        ## -- the icons
        _zz_sheet = [l.strip() for l in open(os.path.join(smoke_env("SMOKE_ROOT", "."), "tools", "icons", "sheet_4.txt"), encoding="utf-8")
                     if l.strip() and not l.startswith("#") and l.strip() != "-"]
        check(len(ICONS) == 114 and len(_zz_sheet) == 26 and all(n in ICONS for n in _zz_sheet)
              and _zz_sheet[:11] == ["place_" + k for k in ZZ_NEW_PLACES]
              and _zz_sheet[11:16] == ["place_" + y for y in PATH_YARD_ICONS]
              and _zz_sheet[16:] == ["bath_soak", "bath_sauna", "pool_swim", "cards_invite", "history", "auto", "save", "help", "continue", "at_home"]
              and all(icon_for("act", i) == i for i in ("bath_soak", "bath_sauna", "pool_swim", "cards_invite")),
              "H: 114 icons; sheet 4 holds the 26 new names in their frozen order; the four new actions have their icon rows", _zz_sheet)
        ## -- with no icon art for a yard, an exit to it draws its area's icon
        _zz_bad = [(y, path_icon(y)) for y in PATH_YARD_ICONS
                   if path_icon(y) != ("place_" + y if icon_has_art("place_" + y) else "area_" + area_of(y))]
        check(not _zz_bad and path_icon("courtyard") == "area_heart" and PATH_HOUSE_EXITS == 7
              and all(len(path_exits(l)) <= 7 for l in LOC_ORDER) and RAIL_MAX <= 8,
              "H: an exit to a yard draws place_<yard> only once that picture is cut, else its area's icon as before (%d of 5 cut today); no place has more than seven exits"
              % len([y for y in PATH_YARD_ICONS if icon_has_art("place_" + y)]), _zz_bad)
        ## -- every validator, together
        _zz_all = [f for fn in (_validate_world, path_validate, hot_validate, view_validate, night_validate, icon_validate, art_validate,
                                rule_validate, _validate_board) for f in fn()]
        check(_zz_all == [], "H: the validators of every file this sitting touched are clean together", _zz_all)

    ## --- I. the picture is what is clicked (D60, 7.3) ------------------------------------
    python:
        settle(day=2, period="Noon", here="courtyard")
        zzc_hold()
        ## The whole section stands in the Courtyard as wave 0 left it: its
        ## own five hotspots at today's points (zzc_court), whatever the real
        ## sidecar holds by now and whatever a later package registered there.
        ZZC_HOLD["shapes0"] = hot_shapes_for("courtyard")
        ZZC_HOLD["n_spots"] = len(HOT_SPOTS)
        zzc_court(trim=True)
        ZZC_REAL[0] = builtins.dict(spots=builtins.dict(ZZC_COURT))
        if ZZC_SHAPED_TREE:
            note("I", "the tree itself shapes %d place(s) by now: the check that no place is shaped stands aside" % len([l for l in LOC_ORDER if hot_shapes_for(l)]))
        _zz_pers = persistent.show_names
        ZZC_HOLD["pers"] = _zz_pers
        persistent.show_names = False

        ## -- the frozen names
        check(zzc_owner(hot_shapes_for, "sb_hotspots.rpy") and zzc_sig(hot_shapes_for) == "(loc)"
              and zzc_owner(hot_tip_rect, "sb_hotspots.rpy") and zzc_sig(hot_tip_rect) == "(key)"
              and isinstance(HOT_SHAPE, builtins.dict)
              and (HOT_SHAPE["polys"], HOT_SHAPE["points"], HOT_SHAPE["area_min"], HOT_SHAPE["area_max"], HOT_SHAPE["buried_max"], HOT_SHAPE["grid"])
              == ((1, 3), (3, 60), 5184, 0.4, 0.5, 4)
              and HOT_LOOK_KEYS == ("color", "wash", "edge", "dim", "names") and all(k in HOT_SHAPE for k in HOT_LOOK_KEYS)
              and HOT_SHAPE["dim"] < 0.5 and 0 < HOT_SHAPE["names"] < 1
              and zzc_sig(hot_layer_rows) == "(loc, front, shapes)" and zzc_screen_params("hot_layer") == ["loc", "front"]
              and builtins.sorted(hot_spots_for("courtyard")[0]) == builtins.sorted(HOT_KEYS) and len(HOT_KEYS) == 11
              and zzc_sig(hot_set_dim) == "(hot_id, fn)",
              "I: hot_shapes_for(loc), hot_tip_rect(key) and HOT_SHAPE live in sb_hotspots.rpy: 1 to 3 polygons of 3 to 60 points, 5,184 px2 to two fifths of the picture, at most half buried, a 4 px grid; the light's five keys; hot_layer keeps its two parameters and hot_spots_for its eleven keys")
        check(hot_shapes_for("courtyard") == {} and (ZZC_SHAPED_TREE or all(hot_shapes_for(l) == {} for l in LOC_ORDER))
              and hot_shapes_for("zz_nowhere") == {} and hot_tip_rect("hot_spot_vend") is None
              and hot_tip_rect("hud_map") is None and hot_tip_rect("hotshape_zz") is None,
              "I: a place whose sidecar holds no shapes is not shaped (the Courtyard with its points alone): hot_shapes_for answers {} and hot_tip_rect None; in the tree as wave 0 ships it that is every place")

        ## -- the counting functions, against the three test shapes
        with open(os.path.join(smoke_env("SMOKE_ROOT", "."), "tools", "smoke", "hot_shape_cases.json"), encoding="utf-8") as _zz_fh:
            _zz_cases = json.load(_zz_fh)
        _zz_pts = builtins.dict((k, builtins.tuple(v)) for k, v in _zz_cases["points"].items())
        _zz_got = hot_shape_count(_zz_cases["shapes"], _zz_pts, builtins.tuple(_zz_cases["size"]), _zz_cases["grid"])
        _zz_got = json.loads(json.dumps(builtins.dict((k, builtins.dict(v)) for k, v in _zz_got.items())))
        check(len(_zz_cases["shapes"]) == 3 and _zz_got == _zz_cases["expect"]
              and builtins.list(hot_shape_order(_zz_cases["shapes"])) == _zz_cases["order"],
              "I: hot_shape_count gives the three test shapes of tools/smoke/hot_shape_cases.json their recorded answers (area, cells, twice, buried, point, under), and hot_shape_order their order",
              [(k, _zz_got.get(k), _zz_cases["expect"].get(k)) for k in _zz_cases["shapes"] if _zz_got.get(k) != _zz_cases["expect"].get(k)])
        _zz_lim = builtins.dict(_zz_cases["limits"], polys=builtins.tuple(_zz_cases["limits"]["polys"]), points=builtins.tuple(_zz_cases["limits"]["points"]))
        _zz_f = builtins.list(hot_shape_findings("zz_cases", _zz_cases["shapes"], None, _zz_pts, builtins.set(_zz_cases["shapes"]),
                                                 builtins.set(_zz_cases["shapes"]), _zz_lim, builtins.tuple(_zz_cases["size"])))
        check(_zz_f == _zz_cases["findings"] and len(_zz_f) == 1
              and builtins.dict((k, HOT_SHAPE[k]) for k in ("area_min", "area_max", "buried_max", "grid")) == builtins.dict((k, _zz_lim[k]) for k in ("area_min", "area_max", "buried_max", "grid"))
              and HOT_SHAPE["polys"] == _zz_lim["polys"] and HOT_SHAPE["points"] == _zz_lim["points"],
              "I: and hot_shape_findings says of them the one sentence recorded there; the file's limits are HOT_SHAPE's", _zz_f)
        with open(os.path.join(smoke_env("SMOKE_ROOT", "."), "game", "sb_hotspots.rpy"), encoding="utf-8") as _zz_fh:
            _zz_src = _zz_fh.read().split("\n")
        _zz_a = [n for n, l in enumerate(_zz_src) if l.strip().startswith("## >>> hot_shape:")]
        _zz_b = [n for n, l in enumerate(_zz_src) if l.strip().startswith("## <<< hot_shape:")]
        _zz_blk = "\n".join(_zz_src[_zz_a[0] + 1:_zz_b[0]]) if len(_zz_a) == 1 and len(_zz_b) == 1 else ""
        check(_zz_blk and all(("def " + n + "(") in _zz_blk for n in ("hot_shape_count", "hot_shape_cells", "hot_shape_order", "hot_shape_inside",
                                                                         "hot_shape_area", "hot_shape_crossed", "hot_shape_findings", "hot_shape_box",
                                                                         "hot_shape_layers"))
              and not any(w in _zz_blk for w in ("renpy", "store.", "config.", "HOT_", "rule_layout", "persistent")),
              "I: the counting and rule functions stand between the two hot_shape marker lines of sb_hotspots.rpy, and that text names nothing of Ren'Py and nothing else of the game (it is copied unchanged into tools/check_layout.py)")

        ## -- the rules in lint: the whole test sidecar is accepted, each broken one refused by name
        zzc_art(courtyard={"rev": 2, "kind": "composed"})
        zzc_d60()
        check(hot_validate() == [] and path_validate() == [] and rule_validate() == [],
              "I: lint accepts the Courtyard's whole test sidecar (four shapes, the gate's and the Training Yard's overlapping; one exit and the two planned things under keep_tile)",
              hot_validate() + path_validate() + rule_validate())
        _zz_broken = [
            ("a point outside its own shape", builtins.dict(shapes={"go_courtyard__dorm_yard": [[[860, 400], [1060, 400], [1060, 520], [860, 520]]]}),
             "go_courtyard__dorm_yard", "outside its own shape"),
            ("a point under a smaller shape", builtins.dict(shapes={"spot_vend": [[[1540, 630], [1700, 630], [1700, 900], [1540, 900]]]}),
             "go_courtyard__training_yard", "under the smaller shape 'spot_vend'"),
            ("a polygon of two points", builtins.dict(shapes={"go_courtyard__gate": [[[1200, 900], [1460, 1040]]]}),
             "go_courtyard__gate", "has 2 points"),
            ("a polygon that crosses itself", builtins.dict(shapes={"go_courtyard__gate": [[[1200, 900], [1460, 1040], [1460, 900], [1200, 1040]]]}),
             "go_courtyard__gate", "crosses itself"),
            ("a shape more than half under smaller ones",
             builtins.dict(shapes={"go_courtyard__gate": [[[1260, 945], [1340, 945], [1340, 1025], [1260, 1025]], [[1400, 795], [1630, 795], [1630, 960], [1400, 960]]]}),
             "go_courtyard__training_yard", "is under smaller shapes"),
            ("a shape smaller than a button", builtins.dict(shapes={"spot_vend": [[[1570, 660], [1630, 660], [1630, 720], [1570, 720]]]}),
             "spot_vend", "smaller than a button"),
            ("a shaped place with one exit that has no shape and is not under keep_tile", builtins.dict(drop=("go_courtyard__dorm_yard",)),
             "go_courtyard__dorm_yard", "has no shape and is not under keep_tile"),
            ## the two layers: the machine is a front hotspot, so its shape is
            ## above every exit's, though here it is the LARGER one (a patch
            ## of empty ground makes it so)
            ("a back hotspot's point under a larger shape of the front layer (a click at the gate's own point would be the machine's)",
             builtins.dict(shapes={"spot_vend": ZZC_SHAPES["spot_vend"] + [[[1000, 500], [1300, 500], [1300, 700], [1000, 700]],
                                                                         [[1280, 965], [1320, 965], [1320, 1005], [1280, 1005]]]}),
             "go_courtyard__gate", "is under the front shape 'spot_vend'"),
            ("a back shape more than half under a larger shape of the front layer",
             builtins.dict(shapes={"spot_vend": ZZC_SHAPES["spot_vend"] + [[[1000, 500], [1300, 500], [1300, 700], [1000, 700]],
                                                                         [[1320, 900], [1460, 900], [1460, 1040], [1320, 1040]]]}),
             "go_courtyard__gate", "is under front shapes and smaller ones"),
        ]
        check(builtins.set(h["id"] for h in HOT_SPOTS if h["place"] == "courtyard" and h["front"]) == {"spot_vend"}
              and zzc_sig(hot_shape_layers) == "(place, shapes, points, front, limits, size)",
              "I: (the Courtyard's one front hotspot is the vending machine; hot_shape_layers(place, shapes, points, front, limits, size) reads the two layers)")
        for _zz_what, _zz_kw, _zz_id, _zz_say in _zz_broken:
            zzc_d60(**_zz_kw)
            _zz_f = hot_validate()
            check(len(_zz_f) == 1 and repr(_zz_id) in _zz_f[0] and _zz_say in _zz_f[0] and "hot_courtyard.json" in _zz_f[0],
                  "I: lint refuses %s, by name" % _zz_what, _zz_f)
        zzc_d60(shapes={"zz_gone": [[[300, 300], [400, 300], [400, 400], [300, 400]]], "gateway": [[[500, 500], [600, 500], [600, 600], [500, 600]]],
                        "go_courtyard__gate": [[[1200, 900], [1460, 900], [1460, 1040], [2000, 1040]]],
                        "spot_vend": [[[1540, 630], [1660, 630], [1660, 750], [1540, 750]], [[1600, 700], [1700, 700], [1700, 780], [1600, 780]]]},
                keep={"go_courtyard__school_yard": "", "straw_posts": "planned", "gateway": "planned", "zz_other": "x"})
        _zz_f = hot_validate()
        check(len(_zz_f) == 7 and any("'zz_gone'" in f and "planned" in f for f in _zz_f) and any("'gateway'" in f and "no point" in f for f in _zz_f)
              and any("'go_courtyard__gate'" in f and "leaves the picture" in f for f in _zz_f) and any("'spot_vend'" in f and "polygons overlap" in f for f in _zz_f)
              and any("keep_tile 'go_courtyard__school_yard'" in f and "reason" in f for f in _zz_f) and any("keep_tile 'gateway'" in f and "shape as well" in f for f in _zz_f)
              and builtins.sum(1 for f in _zz_f if "keep_tile 'zz_other'" in f) == 1,
              "I: and the rest of the rules: a shape for an id that is neither registered nor planned, a planned id with a shape and no point, a polygon that leaves the picture, two polygons of one shape that overlap, a keep_tile row with no reason, one that has a shape as well, one for an unknown id", _zz_f)
        zzc_layout(HOT_LOOK_FILE, {"color": "warm", "wash": 2, "zz_key": 1, "names": 0.25})
        _zz_f = hot_validate()
        zzc_d60()
        check(len(_zz_f) >= 3 and builtins.sum(1 for f in _zz_f if f.startswith("hot_look.json")) == 3
              and hot_look() == builtins.dict(color=HOT_SHAPE["color"], wash=HOT_SHAPE["wash"], edge=HOT_SHAPE["edge"], dim=HOT_SHAPE["dim"], names=0.25),
              "I: lint refuses a hot_look.json with an unknown key, a colour that is not #rrggbb and a strength outside 0 to 1, and the game then keeps its own value for each", _zz_f)
        zzc_layout(HOT_LOOK_FILE, None)
        ## two hotspots at one point share one shape (the storehouse's racks and armory)
        _zz_one = [[[1560, 560], [1640, 560], [1640, 640], [1560, 640]]]
        _zz_store = rule_layout("hot_storehouse")
        _zz_store_real = rule_layout("hot_storehouse")
        _zz_ex = path_exits("storehouse")[0]
        _zz_store.pop("for_rev", None)
        _zz_store.setdefault("spots", {}).update({"racks": [1600, 600], "armory": [1600, 600],
                                                  "go_storehouse__training_yard": [_zz_ex["x"], _zz_ex["y"]]})
        _zz_store["shapes"] = {"racks": _zz_one, "armory": _zz_one,
                               "go_storehouse__training_yard": [[[_zz_ex["x"] - 40, _zz_ex["y"] - 40], [_zz_ex["x"] + 40, _zz_ex["y"] - 40],
                                                                 [_zz_ex["x"] + 40, _zz_ex["y"] + 40], [_zz_ex["x"] - 40, _zz_ex["y"] + 40]]]}
        ## everything else there keeps its button: what is planned, and
        ## whatever a later package has registered
        _zz_store["keep_tile"] = builtins.dict((i, "test: keeps its button") for i in
                                               builtins.set(r[0] for r in SPOT_PLANNED if r[1] == "storehouse")
                                               | builtins.set(h["id"] for h in HOT_SPOTS if h["place"] == "storehouse" and not builtins.str(h["id"]).startswith("zz"))
                                               if i not in _zz_store["shapes"])
        zzc_layout("hot_storehouse", _zz_store)
        _zz_pp = hot_place_points("storehouse")
        check(_zz_pp["racks"] == _zz_pp["armory"] and hot_validate() == [],
              "I: two hotspots registered at one point and never offered together (the storehouse's racks and armory) carry the same polygons, and nothing is read between the two",
              hot_validate())
        zzc_layout("hot_storehouse", _zz_store_real)

        ## -- the gates: when a place is shaped
        zzc_d60()
        _zz_want = builtins.dict((k, v) for k, v in ZZC_SHAPES.items())
        check(hot_shapes_for("courtyard") == _zz_want and hot_shapes_for("courtyard") is not hot_shapes_for("courtyard")
              and isinstance(hot_shapes_for("courtyard")["spot_vend"][0][0], builtins.list),
              "I: with its picture at revision 2 and shapes in its sidecar the Courtyard is shaped: hot_shapes_for returns {id: [polygon, ...]}, a polygon a list of [x, y], a fresh copy each call")
        zzc_art(courtyard={"rev": 1})
        _zz_a = hot_shapes_for("courtyard")
        zzc_art(courtyard=None)
        _zz_b = hot_shapes_for("courtyard")
        zzc_art(courtyard={"rev": 2, "kind": "composed"})
        zzc_d60(for_rev=3)
        _zz_c = hot_shapes_for("courtyard")
        _zz_cf = rule_validate()
        zzc_d60(for_rev=2)
        _zz_d = hot_shapes_for("courtyard")
        check(_zz_a == {} and _zz_b == {} and _zz_c == {} and len(_zz_cf) == 1 and "hot_courtyard" in _zz_cf[0] and _zz_d == _zz_want,
              "I: the same sidecar with the manifest at revision 1, with no manifest row, and with a for_rev that does not match (which lint reports) shapes nothing; a for_rev that matches does",
              (_zz_a, _zz_b, _zz_c, _zz_cf))
        zzc_d60()
        _zz_room = rule_layout("hot_dorm")
        _zz_room_real = rule_layout("hot_dorm")
        _zz_room_row = ART_PICTURES.get("your_room")
        _zz_room.pop("for_rev", None)
        _zz_room["shapes"] = {"computer": [[[400, 550], [480, 550], [480, 630], [400, 630]]]}
        zzc_layout("hot_dorm", _zz_room)
        zzc_art(your_room=None)
        _zz_a = hot_shapes_for("dorm")
        zzc_art(dorm={"rev": 2})
        _zz_b = hot_shapes_for("dorm")
        zzc_art(dorm=None, your_room={"rev": 2})
        _zz_c = hot_shapes_for("dorm")
        check(_zz_a == {} and _zz_b == {} and builtins.list(_zz_c) == ["computer"] and art_stem("dorm") == "your_room",
              "I: My Room is shaped by its picture's file stem: a manifest row for your_room at revision 2 shapes it, and a row named dorm does not (K1)")
        zzc_art(your_room=_zz_room_row)
        zzc_layout("hot_dorm", _zz_room_real)

        ## -- the Courtyard with buttons, as today (the manifest at revision 1): what a shaped one is compared with
        zzc_art(courtyard={"rev": 1})
        zzc_alone("courtyard")
        zzc_unfocus()
        _zz_ids = [h["id"] for h in hot_spots_for("courtyard")]
        _zz_sq0 = builtins.dict((i, zz_rect("sb_place", "hot_" + i)) for i in _zz_ids)
        _zz_act0 = builtins.dict((i, zzc_action("hot_" + i)) for i in _zz_ids)
        _zz_tip0 = builtins.dict((i, renpy.get_displayable("sb_place", "hot_" + i)._tooltip) for i in _zz_ids)
        _zz_btn0 = zz_buttons("sb_place")
        check(len(_zz_ids) == 5 and all(zzc_icons_under("hot_" + i) == 1 for i in _zz_ids) and zzc_fn_transforms().count("hot_pulse_fn") == 5
              and not any(renpy.get_displayable("sb_place", "hotshape_" + i) is not None for i in _zz_ids) and zzc_lights() == {},
              "I: with the same sidecar and the manifest at revision 1 the Courtyard draws its five buttons as today: an icon on a pulsing ring each, and no shape",
              ([zzc_icons_under("hot_" + i) for i in _zz_ids], zzc_fn_transforms()))
        _zz_fn0 = zzc_fn_transforms()
        shot("d60_buttons")

        ## -- the shaped Courtyard
        zzc_art(courtyard={"rev": 2, "kind": "composed"})
        zzc_d60()
        zzc_alone("courtyard")
        zzc_unfocus()
        _zz_shaped = [i for i in _zz_ids if i in ZZC_SHAPES]
        check([h["id"] for h in hot_spots_for("courtyard")] == _zz_ids and len(_zz_shaped) == 4
              and all(zzc_icons_under("hot_" + i) == 0 for i in _zz_shaped) and zzc_fn_transforms().count("hot_pulse_fn") == 1
              and zzc_icons_under("hot_go_courtyard__school_yard") == 1 and zzc_lights() == {}
              and zzc_fn_transforms() == builtins.sorted([f for f in _zz_fn0 if f != "hot_pulse_fn"] + ["hot_pulse_fn"]),
              "I: shaped, no ring and no icon is drawn for a hotspot that has a shape, and nothing is lit until the pointer is on one; the exit under keep_tile is drawn as its button, on its ring",
              ([zzc_icons_under("hot_" + i) for i in _zz_ids], zzc_fn_transforms(), zzc_lights()))
        check(builtins.dict((i, zz_rect("sb_place", "hot_" + i)) for i in _zz_ids) == _zz_sq0
              and builtins.dict((i, zzc_action("hot_" + i)) for i in _zz_ids) == _zz_act0
              and builtins.dict((i, renpy.get_displayable("sb_place", "hot_" + i)._tooltip) for i in _zz_ids) == _zz_tip0
              and all(zzc_alpha("hot_" + i) == 1.0 for i in _zz_ids),
              "I: each hotspot keeps its 72 px square at its point, with its id hot_<id>, its action and its hover label under the key hot_<id>, inside today's alpha wrapper",
              builtins.dict((i, zz_rect("sb_place", "hot_" + i)) for i in _zz_ids))
        check(all(zz_rect("sb_place", "hotshape_" + i) == hot_shape_box(hot_shape_rows("courtyard")[i]) for i in _zz_shaped)
              and all(zzc_action("hotshape_" + i) == _zz_act0[i] == zzc_action("hot_" + i) for i in _zz_shaped)
              and all(renpy.run(renpy.get_displayable("sb_place", "hotshape_" + i).action) == renpy.run(renpy.get_displayable("sb_place", "hot_" + i).action)
                      == (("act", "spot_vend") if i == "spot_vend" else ("act", "path_" + i.split("__")[1])) for i in _zz_shaped)
              and all(renpy.get_displayable("sb_place", "hotshape_" + i)._tooltip == (_zz_tip0[i][0], "hotshape_" + i) for i in _zz_shaped)
              and all(renpy.get_displayable("sb_place", "hotshape_" + i).style.keyboard_focus is False
                      and renpy.get_displayable("sb_place", "hot_" + i).style.keyboard_focus is not False for i in _zz_shaped)
              and renpy.get_displayable("sb_place", "hotshape_go_courtyard__school_yard") is None
              and zz_buttons("sb_place") == _zz_btn0 + 4,
              "I: its shape is a second focus area, hotshape_<id>, the size of the shape's box: pressing it and pressing hot_<id> return the same value; it says the same words under the key hotshape_<id>; the keyboard skips it and not the square",
              [(i, zz_rect("sb_place", "hotshape_" + i), zzc_action("hotshape_" + i)) for i in _zz_shaped])
        _zz_keys = [d._tooltip[1] for d in zzc_tree(renpy.get_screen("sb_place")) if isinstance(getattr(d, "_tooltip", None), builtins.tuple)]
        check(len(_zz_keys) == len(builtins.set(_zz_keys)) and "hotshape_spot_vend" in _zz_keys and "hot_spot_vend" in _zz_keys,
              "I: every tooltip key on the shaped place view is unique (%d)" % len(_zz_keys), [k for k in _zz_keys if _zz_keys.count(k) > 1])
        ## what takes a click, point by point
        check(zzc_at(960, 310) == "hotshape_go_courtyard__dorm_yard" and zzc_at(1040, 400) == "hotshape_go_courtyard__dorm_yard"
              and zzc_at(1600, 690) == "hotshape_spot_vend" and zzc_at(1700, 850) == "hotshape_go_courtyard__training_yard"
              and zzc_at(84, 600) == "hot_go_courtyard__school_yard",
              "I: a click inside a shape is the shape's, anywhere in it and at its hotspot's point too (the empty square takes no pointer); the exit that keeps its button is clicked on its button",
              [zzc_at(960, 310), zzc_at(1040, 400), zzc_at(1600, 690), zzc_at(1700, 850), zzc_at(84, 600)])
        check(zzc_at(700, 500) is None and zzc_at(1080, 330) is None and zzc_at(1180, 950) is None and zzc_at(1500, 780) is None
              and zzc_at(880, 400) is None and hot_overlap((880, 400, 1, 1), zz_rect("sb_place", "hotshape_go_courtyard__dorm_yard")),
              "I: a point outside every polygon focuses nothing: beside a shape, and inside a shape's box but outside its polygon (the garden's is not a rectangle)",
              [zzc_at(700, 500), zzc_at(1080, 330), zzc_at(1180, 950), zzc_at(1500, 780), zzc_at(880, 400)])
        check(zzc_at(1420, 930) == "hotshape_go_courtyard__gate" and zzc_at(1300, 985) == "hotshape_go_courtyard__gate"
              and zzc_at(1500, 930) == "hotshape_go_courtyard__training_yard"
              and hot_shape_order(hot_shape_rows("courtyard"))[:1] == ["spot_vend"]
              and [h["id"] for h in hot_layer_rows("courtyard", False, hot_shape_rows("courtyard"))]
              == ["go_courtyard__training_yard", "go_courtyard__gate", "go_courtyard__dorm_yard", "go_courtyard__school_yard"],
              "I: where two shapes of one layer overlap the smaller takes the click (the gate's over the Training Yard's); the larger is drawn first and a hotspot with no shape last",
              [zzc_at(1420, 930), zzc_at(1500, 930), [h["id"] for h in hot_layer_rows("courtyard", False, hot_shape_rows("courtyard"))]])
        ## the HUD's row: a traced shape may reach under the date and the
        ## chips, and takes no pointer there
        zzc_d60(shapes={"go_courtyard__dorm_yard": ZZC_SHAPES["go_courtyard__dorm_yard"] + [[[600, 0], [700, 0], [700, 160], [600, 160]]]})
        _zz_top = [zzc_at(650, y) for y in (20, 60, HOT_SHAPE["top"] - 1, HOT_SHAPE["top"] + 1, 130)]
        _zz_topbox = zz_rect("sb_place", "hotshape_go_courtyard__dorm_yard")
        zzc_d60()
        zz_render(0.2)
        check(HOT_SHAPE["top"] == 92 and _zz_top == [None, None, None, "hotshape_go_courtyard__dorm_yard", "hotshape_go_courtyard__dorm_yard"]
              and _zz_topbox is not None and _zz_topbox[1] == 0 and all(HOT_SHAPE["top"] <= lane[1] for lane in HOT_LANES)
              and HOT_SHAPE["top"] < HOT_BOUNDS[1] - HOT_SIZE // 2,
              "I: a shape that reaches into the HUD's row takes no pointer there (above y %d, HOT_SHAPE's top) and takes it just below; no hotspot's point can be that high"
              % HOT_SHAPE["top"], (_zz_top, _zz_topbox))
        ## the pointer itself on a shape
        _zz_how = zzc_point(1640, 730, "hotshape_spot_vend")
        note("I: the pointer on a shape", {"pointer": "the window took the pointer: the real hover was read", "focus": "the window was not in front and took no pointer: the engine's own pick at that point (the shape) was focused instead",
                                             "missed": "the engine picked something else at that point"}[_zz_how])
        _zz_tip = GetTooltip()
        _zz_lab = zzc_label_rect()
        _zz_lit = zzc_lights()
        shot("d60_lit_pointer", wait=0)
        check(_zz_how in ("pointer", "focus") and _zz_tip == (_zz_tip0["spot_vend"][0], "hotshape_spot_vend")
              and builtins.list(_zz_lit) == ["spot_vend"]
              and _zz_lit["spot_vend"] == {"dark": (round(min(1.0, 0.75 * HOT_SHAPE["edge"]), 3), 0.0, 3.0), "glow": (HOT_SHAPE["wash"], 1.0, float(HOT_SHAPE["blur"])),
                                           "line": (HOT_SHAPE["edge"], 0.0, 1.0)},
              "I: with the pointer inside a shape (away from its square) the shape is lit at full strength and no other is: a dark rim, a wash that is ADDED to the picture by the outer transform with the blur inside it, and the outline (hover check: needs the pointer)",
              (_zz_tip, _zz_lit))
        check(hot_tip_rect("hotshape_spot_vend") == hot_tip_rect("hot_spot_vend") == _zz_sq0["spot_vend"] and _zz_lab is not None
              and _zz_lab[0] + _zz_lab[2] <= _zz_sq0["spot_vend"][0] + 1 and _zz_lab[1] == _zz_sq0["spot_vend"][1]
              and _zz_tip0["spot_vend"][0].split("\n")[0] in zz_texts("hover_label"),
              "I: and its name opens against the 72 px square at its point, on the side a button's name opens (left of the vending machine), not against the pointer or the shape's box (hover check: needs the pointer)",
              (_zz_lab, _zz_sq0["spot_vend"]))
        zzc_unfocus()
        ## the square, focused as the keyboard would
        zzc_focus("hot_spot_vend")
        _zz_tip2 = GetTooltip()
        _zz_lab2 = zzc_label_rect()
        _zz_lit2 = zzc_lights()
        check(_zz_tip2 == _zz_tip0["spot_vend"] and _zz_lab2 == _zz_lab and _zz_lit2 == _zz_lit,
              "I: with the square focused by renpy.set_focus the same name opens in the same place and the shape is lit the same (hover check: needs the pointer)",
              (_zz_tip2, _zz_lab2, _zz_lab, _zz_lit2))
        zzc_focus("hot_go_courtyard__dorm_yard")
        _zz_lab3 = zzc_label_rect()
        check(builtins.list(zzc_lights()) == ["go_courtyard__dorm_yard"] and _zz_lab3 is not None
              and _zz_lab3[1] + _zz_lab3[3] <= _zz_sq0["go_courtyard__dorm_yard"][1] + 1 and _zz_lab3[0] == _zz_sq0["go_courtyard__dorm_yard"][0]
              and icon_tip_side(("x", "hotshape_go_courtyard__dorm_yard")) == icon_tip_side(("x", "hot_go_courtyard__dorm_yard")) == "top"
              and icon_tip_side(("x", "hotshape_spot_vend")) == icon_tip_side(("x", "hot_spot_vend")) == "left",
              "I: an exit's name opens above its square, as its button's does, and the side is the same for either of its two keys",
              (_zz_lab3, _zz_sq0["go_courtyard__dorm_yard"]))
        shot("d60_lit_exit", wait=0)
        zzc_unfocus()
        check(zzc_lights() == {} and GetTooltip() is None, "I: with the focus gone nothing is lit")

        ## -- a locked exit, an action the night shuts, a dim function
        ZZC_HOLD["path_locked"] = store.path_locked
        store.path_locked = zz_d60_locked
        renpy.restart_interaction()
        zzc_focus("hot_go_courtyard__dorm_yard")
        _zz_dimmed = builtins.dict(dark=round(min(1.0, 0.75 * HOT_SHAPE["edge"]) * HOT_SHAPE["dim"], 3), glow=round(HOT_SHAPE["wash"] * HOT_SHAPE["dim"], 3),
                                   line=round(HOT_SHAPE["edge"] * HOT_SHAPE["dim"], 3))
        _zz_l = zzc_lights().get("go_courtyard__dorm_yard", {})
        check(GetTooltip() == ("The garden gate is barred.", "hot_go_courtyard__dorm_yard")
              and builtins.dict((k, v[0]) for k, v in _zz_l.items()) == _zz_dimmed
              and zzc_alpha("hot_go_courtyard__dorm_yard") == HOT_DIM_ALPHA
              and zzc_action("hot_go_courtyard__dorm_yard")[0] == zzc_action("hotshape_go_courtyard__dorm_yard")[0] == "NullAction"
              and renpy.get_displayable("sb_place", "hotshape_go_courtyard__dorm_yard")._tooltip == ("The garden gate is barred.", "hotshape_go_courtyard__dorm_yard")
              and zzc_at(960, 310) == "hotshape_go_courtyard__dorm_yard",
              "I: a locked exit lights dimmed (under half strength), its square and its shape both say the lock's reason, and neither does anything; its square is in the alpha wrapper at 0.45",
              (GetTooltip(), _zz_l))
        shot("d60_locked", wait=0)
        zzc_unfocus()
        store.path_locked = ZZC_HOLD["path_locked"]
        hot_set_dim("spot_vend", "zz_dim_test")
        ZZC_DIM[0] = "Sold out till morning."
        renpy.restart_interaction()
        zzc_focus("hotshape_spot_vend")
        _zz_l = zzc_lights().get("spot_vend", {})
        check(GetTooltip() == ("Sold out till morning.", "hotshape_spot_vend") and builtins.dict((k, v[0]) for k, v in _zz_l.items()) == _zz_dimmed
              and zzc_action("hot_spot_vend")[0] == zzc_action("hotshape_spot_vend")[0] == "NullAction" and zzc_alpha("hot_spot_vend") == HOT_DIM_ALPHA
              and "Sold out till morning." in zz_texts("hover_label"),
              "I: a test dim function's reason is said by the shape, which lights dimmed and does nothing", (GetTooltip(), _zz_l))
        zzc_unfocus()
        ZZC_DIM[0] = ""
        HOT_DIM.clear()
        HOT_DIM.update(ZZC_HOLD["dim"])
        ## an action the night has shut: none of the Courtyard's is (walking
        ## is free and the machine has no cost), so the Library is shaped
        ## for it, as the overlay that shapes every place shapes it
        _zz_lib_row = ART_PICTURES.get("library")
        _zz_lib_before = hot_shapes_for("library")
        if art_rev("library") < 2:
            zzc_art(library={"rev": 2, "kind": "composed"})
        _zz_lib_real = zzc_squares("library")
        zzc_alone("library", "Night")
        zzc_unfocus()
        _zz_night = [h["id"] for h in hot_spots_for("library") if h["id"] in hot_shapes_for("library") and not hot_open(h)]
        check("stacks" in _zz_night and hot_validate() == [] and not path_locked("library")
              and renpy.get_displayable("sb_place", "hotshape_stacks") is not None and zzc_icons_under("hot_stacks") == 0,
              "I: (the Library, shaped by a square round each of its points, at Night: its stacks are shown and shut, and lint is clean)",
              (_zz_night, [h["id"] for h in hot_spots_for("library")], hot_validate()))
        zzc_focus("hot_stacks")
        _zz_l = zzc_lights().get("stacks", {})
        check(GetTooltip() == ("Too late. Bed.", "hot_stacks") and builtins.dict((k, v[0]) for k, v in _zz_l.items()) == _zz_dimmed
              and renpy.get_displayable("sb_place", "hotshape_stacks")._tooltip == ("Too late. Bed.", "hotshape_stacks")
              and zzc_action("hot_stacks")[0] == zzc_action("hotshape_stacks")[0] == "NullAction" and zzc_alpha("hot_stacks") == HOT_DIM_ALPHA
              and "Too late. Bed." in zz_texts("hover_label"),
              "I: an action the night has shut (the Library's stacks at Night) lights dimmed, its square and its shape both say \"Too late. Bed.\", and neither does anything",
              (GetTooltip(), _zz_l, zzc_action("hot_stacks"), zzc_action("hotshape_stacks")))
        shot("d60_night_shut", wait=0)
        zzc_unfocus()
        zzc_layout("hot_library", _zz_lib_real)
        zzc_art(library=_zz_lib_row)
        check(hot_shapes_for("library") == _zz_lib_before and hot_validate() == [],
              "I: (the Library put back: its shapes are what they were before the test)", hot_validate())
        zzc_alone("courtyard")
        zzc_unfocus()

        ## -- names shown: every shape lit, each with its name against its square
        persistent.show_names = True
        store.path_faces = zz_d60_faces
        renpy.restart_interaction()
        zz_render(0.4)
        _zz_l = zzc_lights()
        _zz_txt = zz_texts("sb_place")
        _zz_rows = builtins.dict((h["id"], h) for h in hot_spots_for("courtyard"))
        _zz_nr = builtins.dict((i, hot_name_rect(_zz_rows[i])) for i in _zz_shaped)
        check(builtins.sorted(_zz_l) == builtins.sorted(_zz_shaped)
              and all(_zz_l[i]["line"][0] == round(HOT_SHAPE["edge"] * HOT_SHAPE["names"], 3) and _zz_l[i]["glow"][0] == round(HOT_SHAPE["wash"] * HOT_SHAPE["names"], 3)
                      for i in _zz_shaped)
              and all(hot_name(_zz_rows[i]) in _zz_txt for i in _zz_ids),
              "I: while names are shown every shape of the place is lit at the reduced strength, and every hotspot and exit is named", (_zz_l, _zz_txt))
        check(all(not hot_overlap(_zz_nr[i], _zz_sq0[i]) and (_zz_nr[i][0] + _zz_nr[i][2] == _zz_sq0[i][0] or _zz_nr[i][1] + _zz_nr[i][3] == _zz_sq0[i][1])
                  for i in _zz_shaped)
              and _zz_nr["go_courtyard__dorm_yard"][0] == _zz_sq0["go_courtyard__dorm_yard"][0]
              and all(0 <= r[0] and r[0] + r[2] <= config.screen_width and 0 <= r[1] for r in _zz_nr.values())
              and not any(hot_overlap(_zz_nr[a], _zz_nr[b]) for a in _zz_shaped for b in _zz_shaped if a < b),
              "I: a shaped hotspot's name is drawn against the square at its point, on the side its hover label opens (hot_name_rect: above an exit, left of the machine), on screen, and no two of the Courtyard's meet",
              _zz_nr)
        ## a `tips` row moves the plate with the hover label, for the place I stand in
        zzc_d60(tips={"spot_vend": "bottom", "go_courtyard__gate": "left"})
        _zz_nt = builtins.dict((i, hot_name_rect(_zz_rows[i])) for i in _zz_shaped)
        store.here = "dorm"
        _zz_nt_away = builtins.dict((i, hot_name_rect(_zz_rows[i])) for i in _zz_shaped)
        store.here = "courtyard"
        zzc_d60()
        check(_zz_nt["spot_vend"][:2] == (_zz_sq0["spot_vend"][0], _zz_sq0["spot_vend"][1] + 72)
              and _zz_nt["go_courtyard__gate"][0] + _zz_nt["go_courtyard__gate"][2] == _zz_sq0["go_courtyard__gate"][0]
              and _zz_nt["go_courtyard__gate"][1] == _zz_sq0["go_courtyard__gate"][1]
              and all(_zz_nt[i] == _zz_nr[i] for i in _zz_shaped if i not in ("spot_vend", "go_courtyard__gate"))
              and _zz_nt_away == _zz_nr and builtins.dict((i, hot_name_rect(_zz_rows[i])) for i in _zz_shaped) == _zz_nr,
              "I: hot_name_rect follows the sidecar's `tips`: a row for the machine puts its plate under its square and one for the gate puts it left of it, the others stay; the row read is the one of the place I stand in (tools/smoke/u2_dump.rpy stands in each place in turn)",
              (_zz_nt, _zz_nr, _zz_nt_away))
        check(zzc_face_count("megumi") == 2 and zzc_face_count("yuji") == 2 and hot_tip_faces("hot_go_courtyard__dorm_yard") == ["megumi", "yuji"]
              and hot_tip_faces("hotshape_go_courtyard__dorm_yard") == ["megumi", "yuji"] and hot_tip_faces("hot_go_courtyard__school_yard") == []
              and hot_tip_faces("hot_spot_vend") == [] and hot_tip_faces("hud_map") == [],
              "I: with path_faces patched to return two people, their faces show beside the shaped exit's name (on its plate) and on the unshaped exit's tile, and nowhere else",
              (zzc_face_count("megumi"), zzc_face_count("yuji")))
        shot("d60_names")
        zzc_focus("hot_go_courtyard__dorm_yard")
        _zz_lf = builtins.sum(1 for d in zzc_tree(renpy.get_screen("hover_label"))
                              if isinstance(d, renpy.display.transform.Transform) and d.crop is not None
                              and builtins.str(getattr(d.child, "filename", "")).startswith("images/side/"))
        _zz_lw = zzc_label_rect()
        check(_zz_lf == 2 and zzc_lights()["go_courtyard__dorm_yard"]["line"][0] == HOT_SHAPE["edge"]
              and icon_tip_size(GetTooltip()) is not None and _zz_lw is not None and abs(icon_tip_size(GetTooltip())[0] - _zz_lw[2]) <= 2,
              "I: under the pointer the hover label draws the two faces beside the shaped exit's name (and is measured with them), and that shape is lit at full strength while the others stay at the names strength",
              (_zz_lf, _zz_lw, icon_tip_size(GetTooltip())))
        shot("d60_names_faces", wait=0)
        zzc_focus("hot_go_courtyard__school_yard")
        _zz_lf = builtins.sum(1 for d in zzc_tree(renpy.get_screen("hover_label"))
                              if isinstance(d, renpy.display.transform.Transform) and d.crop is not None
                              and builtins.str(getattr(d.child, "filename", "")).startswith("images/side/"))
        check(_zz_lf == 0, "I: an exit that keeps its button shows the faces on its tile, and its hover label draws none", _zz_lf)
        zzc_unfocus()
        ## the worst case (R6) for the shaped place view: names, faces, four toasts, the banner
        zz_worst("sb_place", name="worst_place_shaped")
        toast_clear()
        persistent.show_names = False
        store.path_faces = ZZC_PF
        renpy.restart_interaction()

        ## -- hidden behind a person: the hotspot is not drawn and its shape takes no click
        HOT_SPOTS.append(builtins.dict(id="zz_d60_look", place="courtyard", x=1300, y=700, icon="look", kind="look", act=None,
                                       lines=["A test line."], label="A test look", hint="", cost=0, when=None, standalone=False, front=False))
        HOT_SPOTS.append(builtins.dict(id="zz_d60_plain", place="courtyard", x=500, y=850, icon="look", kind="look", act=None,
                                       lines=["A test line."], label="A test button", hint="", cost=0, when=None, standalone=False, front=False))
        zzc_d60(shapes={"zz_d60_look": [[[1250, 650], [1350, 650], [1350, 750], [1250, 750]]]})
        zzc_alone("courtyard")
        zzc_unfocus()
        check(hot_validate() == [] and zzc_at(1300, 700) == "hotshape_zz_d60_look" and zzc_at(1300, 985) == "hotshape_go_courtyard__gate"
              and zzc_icons_under("hot_zz_d60_plain") == 1 and zzc_at(500, 850) == "hot_zz_d60_plain"
              and renpy.get_displayable("sb_place", "hotshape_zz_d60_plain") is None,
              "I: lint is clean with a harness's own zz hotspots registered in the shaped place: one with a shape is clicked on its shape, and one without is drawn as its button",
              hot_validate())
        ZZC_HOLD["view_person_rects"] = store.view_person_rects
        ZZC_HOLD["rect"] = (1240, 680, 120, 330)
        store.view_person_rects = zz_d60_rects
        renpy.restart_interaction()
        zz_render(0.4)
        _zz_now = [h["id"] for h in hot_spots_for("courtyard")]
        _zz_offer = [d.action.value for d in zzc_tree(renpy.get_screen("sb_place"))
                     if isinstance(getattr(d, "action", None), Return) and isinstance(d.action.value, builtins.tuple)]
        check("go_courtyard__gate" not in _zz_now and "zz_d60_look" not in _zz_now and "spot_vend" in _zz_now
              and all(renpy.get_displayable("sb_place", w + i) is None for w in ("hot_", "hotshape_") for i in ("go_courtyard__gate", "zz_d60_look"))
              and zzc_at(1300, 985) is None and zzc_at(1300, 700) is None and zzc_at(1420, 930) == "hotshape_go_courtyard__training_yard"
              and "path_gate" in [a[0] for a in rail_actions("courtyard")] and ("act", "path_gate") in _zz_offer
              and not any(v[0] == "hot" and v[1] == "zz_d60_look" for v in _zz_offer),
              "I: with a person's rectangle over a hotspot's square the hotspot is not drawn and its shape takes no click (the shape under it does); an exit's row is then in the column, and a look is offered nowhere",
              (_zz_now, zzc_at(1300, 985), zzc_at(1300, 700), [a[0] for a in rail_actions("courtyard")]))
        store.view_person_rects = ZZC_HOLD["view_person_rects"]

        ## -- layers: a front shape over a person; a back shape under a pose's box and under the foreground cut-out
        zzc_alone("courtyard")
        pin("megumi", "courtyard")
        renpy.restart_interaction()
        zz_render(0.4)
        _zz_pr = zz_rect("sb_place", "stage_megumi")
        _zz_px, _zz_py = int(_zz_pr[0] + _zz_pr[2] / 2), int(_zz_pr[1] + _zz_pr[3] * 0.45)
        _zz_who0 = zzc_at(_zz_px, _zz_py)
        _zz_patch = [[_zz_px - 60, _zz_py - 60], [_zz_px + 60, _zz_py - 60], [_zz_px + 60, _zz_py + 60], [_zz_px - 60, _zz_py + 60]]
        _zz_back = [h["id"] for h in hot_spots_for("courtyard") if h["id"] in ZZC_SHAPES and not h["front"]][0]
        zzc_d60(shapes={_zz_back: ZZC_SHAPES[_zz_back] + [_zz_patch]})
        _zz_who1 = zzc_at(_zz_px, _zz_py)
        _zz_beside = [(x, _zz_py) for x in (_zz_px - 58, _zz_px + 58) if zzc_at(x, _zz_py) == "hotshape_" + _zz_back]
        zzc_d60(shapes={"spot_vend": ZZC_SHAPES["spot_vend"] + [_zz_patch]})
        _zz_who2 = zzc_at(_zz_px, _zz_py)
        check(_zz_who0 == "stage_megumi" and _zz_who1 == "stage_megumi" and _zz_who2 == "hotshape_spot_vend" and zzc_at(1600, 690) == "hotshape_spot_vend",
              "I: a back shape is under the people (a click on a standing person's own pixels is the person's), and a front shape takes the click over a person standing inside it",
              (_zz_pr, _zz_who0, _zz_who1, _zz_who2, _zz_beside))
        shot("d60_person")
        pin("megumi", "-")
        ## a painted pose is a button over its whole box
        ZZC_HOLD["view_stage_rows"] = store.view_stage_rows
        ZZC_HOLD["pose"] = (1400, 800, 200, 150)
        ZZC_HOLD["pose_image"] = "images/bg/courtyard.png"
        zzc_d60()
        store.view_stage_rows = zz_d60_rows
        renpy.restart_interaction()
        zz_render(0.4)
        _zz_under = [h["id"] for h in hot_spots_for("courtyard")]
        check("go_courtyard__training_yard" in _zz_under and zzc_at(1450, 830) == "stage_megumi" and zzc_at(1700, 830) == "hotshape_go_courtyard__training_yard",
              "I: a back shape takes no click under a test pose's box (the pose is a button over its whole box) and takes it beside the box",
              (_zz_under, zzc_at(1450, 830), zzc_at(1700, 830)))
        store.view_stage_rows = ZZC_HOLD["view_stage_rows"]
        ## the room's foreground cut-out: its own pixels cover a back shape, and it is no button
        ZZC_HOLD["fg"] = "images/fg/fg_dorm_common.png"
        _zz_surf = renpy.load_surface(ZZC_HOLD["fg"])
        _zz_on = [(x, y) for y in range(300, 1040, 20) for x in range(200, 1300, 20) if _zz_surf.get_at((x, y))[3] == 255][:1]
        _zz_off = [(x, y) for y in range(300, 1040, 20) for x in range(200, 1300, 20) if _zz_surf.get_at((x, y))[3] == 0][:1]
        if check(len(_zz_on) == 1 and len(_zz_off) == 1 and _zz_surf.get_size() == (1920, 1080), "I: (a test foreground cut-out with a covered and a clear point)", (_zz_on, _zz_off)):
            _zz_cut = [[[x - 12, y - 12], [x + 12, y - 12], [x + 12, y + 12], [x - 12, y + 12]] for x, y in (_zz_on[0], _zz_off[0])]
            zzc_d60(shapes={"go_courtyard__dorm_yard": ZZC_SHAPES["go_courtyard__dorm_yard"] + _zz_cut,
                            "spot_vend": ZZC_SHAPES["spot_vend"]})
            _zz_b0 = (zzc_at(*_zz_on[0]), zzc_at(*_zz_off[0]))
            ZZC_HOLD["view_fg_path"] = store.view_fg_path
            store.view_fg_path = zz_d60_fg
            renpy.restart_interaction()
            zz_render(0.4)
            _zz_b1 = (zzc_at(*_zz_on[0]), zzc_at(*_zz_off[0]))
            zzc_d60(shapes={"spot_vend": ZZC_SHAPES["spot_vend"] + _zz_cut})
            _zz_b2 = (zzc_at(*_zz_on[0]), zzc_at(*_zz_off[0]))
            store.view_fg_path = ZZC_HOLD["view_fg_path"]
            check(_zz_b0 == ("hotshape_go_courtyard__dorm_yard", "hotshape_go_courtyard__dorm_yard") and _zz_b1 == (None, "hotshape_go_courtyard__dorm_yard")
                  and _zz_b2 == ("hotshape_spot_vend", "hotshape_spot_vend"),
                  "I: a back shape takes no click where a test foreground cut-out covers it and takes it where the cut-out is clear; a front shape is in front of the cut-out",
                  (_zz_b0, _zz_b1, _zz_b2))
        zzc_d60()
        HOT_SPOTS[:] = [h for h in HOT_SPOTS if not builtins.str(h["id"]).startswith("zz_d60_")]
        check(not any(builtins.str(h["id"]).startswith("zz_d60_") for h in HOT_SPOTS) and hot_validate() == [], "I: (the test hotspots taken out again)", hot_validate())

        ## -- the light itself: on a white patch and on a black one; hot_look.json
        renpy.hide_screen("sb_place")
        _zz_box = hot_shape_box(hot_shape_rows("courtyard")["go_courtyard__dorm_yard"])
        _zz_area = (_zz_box[0] - 10, _zz_box[1] + 60, _zz_box[2] + 20, _zz_box[3] - 50)     # the label lies over the box's top
        _zz_px = builtins.dict()
        for _zz_col, _zz_nm in (("#ffffff", "white"), ("#000000", "black")):
            renpy.show_screen("zz_d60_patch", _zz_col)
            zzc_unfocus()
            shot("d60_%s_unlit" % _zz_nm)
            zzc_focus("hot_go_courtyard__dorm_yard", "zz_d60_patch")
            _zz_onp = builtins.list(zzc_lights("zz_d60_patch"))
            shot("d60_%s_lit" % _zz_nm, wait=0)
            zzc_unfocus()
            renpy.hide_screen("zz_d60_patch")
            _zz_px[_zz_nm] = (zzc_pixel_diff("d60_%s_unlit" % _zz_nm, "d60_%s_lit" % _zz_nm, _zz_area), _zz_onp)
        check(all(_zz_px[n][0] >= 300 and _zz_px[n][1] == ["go_courtyard__dorm_yard"] for n in ("white", "black")) and _zz_px["black"][0] > _zz_px["white"][0],
              "I: a lit and an unlit frame differ measurably on a white test patch (%d pixels: the outline and its dark rim) and on a black one (%d: the wash as well) (hover check: needs the pointer)"
              % (_zz_px["white"][0], _zz_px["black"][0]), _zz_px)
        zzc_alone("courtyard")
        zzc_focus("hot_spot_vend")
        _zz_l0 = zzc_lights()["spot_vend"]
        zzc_layout(HOT_LOOK_FILE, {"wash": 0.6, "edge": 0.5, "color": "#aaccff"})
        renpy.restart_interaction()
        zz_render(0.4)
        _zz_l1 = zzc_lights()["spot_vend"]
        _zz_c1 = [d.color for d in zzc_tree(renpy.get_screen("sb_place")) if isinstance(d, hot_ShapeLight) and d.part == "wash"]
        _zz_v1 = hot_validate()
        zzc_layout(HOT_LOOK_FILE, None)
        renpy.restart_interaction()
        zz_render(0.4)
        _zz_l2 = zzc_lights()["spot_vend"]
        zzc_unfocus()
        check(_zz_l0["glow"][0] == HOT_SHAPE["wash"] and _zz_l1["glow"][0] == 0.6 and _zz_l1["line"][0] == 0.5 and _zz_c1 == ["#aaccff"] and _zz_v1 == []
              and _zz_l2 == _zz_l0 and hot_look() == builtins.dict((k, HOT_SHAPE[k]) for k in HOT_LOOK_KEYS),
              "I: a test hot_look.json changes the light's strength and colour, and its absence leaves HOT_SHAPE's", (_zz_l0, _zz_l1, _zz_l2))

        ## -- saves and motion
        _zz_pk = renpy.compat.pickle
        _zz_shape = hot_shape_rows("courtyard")["spot_vend"]
        _zz_one = _zz_pk.loads(_zz_pk.dumps(hot_ShapeLight(_zz_shape, hot_shape_box(_zz_shape), hot_light_pad(), "wash", "#fff0cc")))
        _zz_fn = _zz_pk.loads(_zz_pk.dumps(renpy.partial(hot_shape_hit, _zz_shape, hot_shape_box(_zz_shape), None)))
        _zz_no = _zz_pk.loads(_zz_pk.dumps(hot_no_point))
        check(type(_zz_one).__name__ == "hot_ShapeLight" and _zz_one.shape == _zz_shape and _zz_one.part == "wash"
              and _zz_fn(60, 60) is True and _zz_fn(-5, 60) is False and _zz_no(0, 0) is False
              and renpy.get_displayable("sb_place", "hot_spot_vend").style.focus_mask is hot_no_point
              and renpy.get_displayable("sb_place", "hotshape_spot_vend").style.focus_mask == renpy.partial(hot_shape_hit, _zz_shape, hot_shape_box(_zz_shape), None),
              "I: an instance of the light's class (a plain top-level class) and the shape's focus function (a curried top-level function) pickle and come back working; the square's focus mask refuses every point")
        check(zzc_fn_transforms() == builtins.sorted([f for f in _zz_fn0 if f != "hot_pulse_fn"] + ["hot_pulse_fn"]) and _zz_fn0.count("hot_pulse_fn") == 5
              and zzc_saved_pictures("", screen="sb_place") >= 1,
              "I: no function transform is added to the place view (the one left is the ring of the exit that keeps its button), and what a save made on the shaped Courtyard would hold pickles and reads back with its place view in it",
              (zzc_fn_transforms(), _zz_fn0, zzc_saved_pictures("", screen="sb_place")))
        zzc_d60(keep=builtins.dict((k, v) for k, v in ZZC_KEEP.items() if k != "go_courtyard__school_yard"),
                shapes={"go_courtyard__school_yard": [[[44, 480], [200, 480], [200, 760], [44, 760]]]})
        zz_render(0.4)
        check(zzc_fn_transforms() == [f for f in _zz_fn0 if f != "hot_pulse_fn"] and hot_validate() == [] and zzc_lights() == {},
              "I: with every hotspot of the Courtyard shaped there is no function transform on its place view at all (the rings' are gone)", zzc_fn_transforms())
        shot("d60_unlit")
        ## -- a save made on the shaped place view loads on it
        zzc_scrub()
    ## (An entry of the rollback log ends at an interaction: two, so the
    ## working variables are in entries of their own, behind the two the
    ## save keeps. The statement that saves runs again after the load, which
    ## is what ZZC_SAVE[0] is for.)
    $ zz_render(0.1)
    $ zz_render(0.1)
    python:
        if ZZC_SAVE[0] == 0:
            zzc_save_load("zzc_d60")
    python:
        zz_render(0.5)
        check(ZZC_SAVE[0] == 2 and zzc_where() == ZZC_SAVE[1] and ZZC_SAVE[1] is not None and ZZC_SAVE[1][3:5] == ("courtyard", True)
              and len(ZZC_SAVE[1][5]) == 5 and not ZZC_RECOVER,
              "I: and it loads on it: the load comes back at the same depth, day, hour and place with the place view up and its five shape widgets on it, and neither load_recover nor return_recover ran",
              (ZZC_SAVE[0], zzc_where(), ZZC_SAVE[1], ZZC_RECOVER))
        zzc_unfocus()
        check(hot_shapes_for("courtyard") and zzc_at(1600, 690) == "hotshape_spot_vend" and zzc_at(1300, 985) == "hotshape_go_courtyard__gate"
              and zzc_at(120, 600) == "hotshape_go_courtyard__school_yard" and zzc_at(700, 500) is None
              and renpy.get_displayable("sb_place", "hot_spot_vend").style.focus_mask is hot_no_point
              and zzc_icons_under("hot_spot_vend") == 0 and zzc_lights() == {} and zzc_fn_transforms().count("hot_pulse_fn") == 0,
              "I: after the load the shapes answer at their points, a point outside every polygon focuses nothing, the square takes no pointer, and no ring or icon is drawn",
              (zzc_at(1600, 690), zzc_at(1300, 985), zzc_at(120, 600), zzc_at(700, 500), zzc_lights()))
        zzc_focus("hot_spot_vend")
        check(builtins.list(zzc_lights()) == ["spot_vend"] and isinstance(GetTooltip(), builtins.tuple) and GetTooltip()[1] == "hot_spot_vend",
              "I: and a shape lights again under the focus (hover check: needs the pointer)", (zzc_lights(), GetTooltip()))
        shot("d60_after_load", wait=0)
        zzc_unfocus()
        if renpy.can_load("zzc_d60"):
            renpy.unlink_save("zzc_d60")

        renpy.hide_screen("sb_place")
        persistent.show_names = ZZC_HOLD["pers"]
        store.schedule_overrides = {}
        zzc_back()
        zzc_court_back()
        check(hot_shapes_for("courtyard") == ZZC_HOLD["shapes0"] and hot_validate() == [] and HOT_DIM == ZZC_HOLD["dim"]
              and len(HOT_SPOTS) == ZZC_HOLD["n_spots"] and "spots" not in ZZC_HOLD,
              "I: (every table put back: the Courtyard's shapes, the dim table and the hotspots are what they were before the section)",
              (hot_validate(), HOT_DIM, len(HOT_SPOTS), ZZC_HOLD["n_spots"]))

    $ finish()
