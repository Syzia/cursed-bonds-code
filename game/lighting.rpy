################################################################################
## Cursed Bonds — lighting the characters to match the place they stand in.
##
## The backgrounds are painted for their hour: a sunset rooftop, a candlelit
## office, a moonlit courtyard. A sprite drawn in flat daylight looks pasted on
## top of them, so every character image is wrapped in `sprite_lit`, which
## tints it by the light of whatever background is showing. The light is set
## whenever a background is shown on the master layer:
##
##   scene expression graded_bg()   -> the campus place and period (`here`, `period`)
##   scene bg city                  -> looked up by the background's name
##
## Sprites made by tools/gen_sprite_defs.py also get a soft contact shadow
## under their feet, so they stand on the floor instead of floating over it.
################################################################################

## (tint, brightness, saturation, shadow opacity). Gentler than the grade the
## background itself gets: faces have to stay readable.
init -10 python:
    import builtins

    NEUTRAL_LIGHT = ("#ffffff", 0.0, 1.0, 0.55)

    OUTDOOR_LIGHT = {
        "Morning":   ("#fff6ec", 0.00, 1.00, 0.55),
        "Noon":      ("#ffffff", 0.00, 1.00, 0.58),
        "Afternoon": ("#fff1e2", 0.00, 1.00, 0.55),
        "Evening":   ("#ffcfa8", -0.03, 0.95, 0.49),
        "Night":     ("#a8b6e8", -0.10, 0.80, 0.41),
    }
    INDOOR_LIGHT = {
        "Morning":   ("#fff8f0", 0.00, 1.00, 0.49),
        "Noon":      ("#ffffff", 0.00, 1.00, 0.49),
        "Afternoon": ("#fff4e8", 0.00, 1.00, 0.49),
        "Evening":   ("#ffe8d0", -0.02, 0.98, 0.47),
        "Night":     ("#e2e4f4", -0.06, 0.92, 0.43),
    }

    ## Places with their own light: (place, picture variant). A variant of None
    ## means the place is lit the same at every hour.
    PLACE_LIGHT = {
        ("office", None):           ("#ffc996", -0.08, 0.90, 0.43),   # candles only
        ("storehouse", None):       ("#eedcc4", -0.06, 0.92, 0.43),   # lamps, one high window
        ("utahime_office", None):   ("#e8eefc", -0.03, 0.95, 0.45),   # paper screens, cool daylight
        ("gojo_office", None):      ("#ffe4ee", 0.00, 1.00, 0.47),    # the television, and sugar
        ("rooftop", "evening"):     ("#ffc7a2", -0.02, 0.97, 0.49),
        ("rooftop", "night"):       ("#a3b3e8", -0.09, 0.80, 0.39),
        ("riverside", "evening"):   ("#ffcf9e", -0.02, 0.97, 0.49),
        ("infirmary", "night"):     ("#fff0e0", -0.03, 0.96, 0.45),
        ("dorm", "night"):          ("#ffdcb0", -0.03, 0.95, 0.45),
        ("dorm_common", "evening"): ("#ffcca6", -0.02, 0.97, 0.47),
        ("dorm_common", "night"):   ("#ffe2bc", -0.02, 0.96, 0.45),
        ("girls_dorm", "night"):    ("#ffe8c8", -0.03, 0.96, 0.45),
    }

    ## Story backgrounds shown by name that aren't daylight.
    BG_LIGHT = {
        "bg city":               ("#b0bbe6", -0.08, 0.85, 0.39),
        "bg veil":               ("#c0b4dc", -0.08, 0.85, 0.39),
        "bg home_bedroom_night": ("#c6cdee", -0.06, 0.88, 0.41),
        ## The placeholder backgrounds (bg_placeholders.rpy).
        "bg alley":              ("#bcc2de", -0.08, 0.80, 0.41),
        "bg alley dark":         ("#ab9cd6", -0.14, 0.70, 0.35),
        "bg ridge_veil":         ("#c4b6e6", -0.08, 0.85, 0.39),
        "bg utahime_office":     ("#e8eefc", -0.03, 0.95, 0.45),
        "bg gojo_office":        ("#ffe4ee", 0.00, 1.00, 0.47),
        "bg map_tokyo":          ("#b0bbe6", -0.08, 0.85, 0.39),
        "bg shibuya":            ("#dcc4ea", -0.06, 0.90, 0.41),
        "bg harajuku":           ("#ffeef6", 0.02, 1.00, 0.55),   # pink daylight
        "bg shinjuku":           ("#b8c8ea", -0.08, 0.85, 0.39),
        "bg kawasaki":           ("#f2eee6", 0.00, 0.88, 0.50),   # bleached daylight
        "bg yotsuka":            ("#fff0e0", 0.00, 1.00, 0.55),
        ## The second overhaul (U0c2, 5.8): the off-campus names that stand
        ## in for a scene's own picture take the light of the picture each
        ## plays over until it is painted (bg city, bg veil; the ruined hall
        ## has no row and neither do its three). A measured row in
        ## game/layout/light.json replaces each with its picture.
        "bg mall_front":         ("#b0bbe6", -0.08, 0.85, 0.39),
        "bg warehouse":          ("#b0bbe6", -0.08, 0.85, 0.39),
        "bg site_platform":      ("#b0bbe6", -0.08, 0.85, 0.39),
        "bg site_karaoke":       ("#b0bbe6", -0.08, 0.85, 0.39),
        "bg mall_atrium":        ("#c0b4dc", -0.08, 0.85, 0.39),
        "bg site_pool":          ("#c0b4dc", -0.08, 0.85, 0.39),
    }

    ## The second UI overhaul (U0c2; docs/UI2_DESIGN.md 6.1, 6.2, K7).
    ##
    ## A row is four values, or six: the same four and then (shadow lean in
    ## px, shadow stretch). A four-value row means (0, 1.0). scene_light may
    ## hold either (an old save holds four); light_matrix reads the first
    ## three of either and _shadow_light the fourth.
    ##
    ## A measured row wins over the tables above:
    ##   game/layout/light_<place>.json   {"": row, "evening": row, "night": row}
    ##                                    for the place's day picture and its
    ##                                    hour pictures (written by the installer)
    ##   game/layout/light.json           {"bg alley": row}: story pictures, by
    ##                                    image name
    ## A place's measured row is used only while it is fresh (art_fresh: it
    ## was measured on the picture that is installed).

    ## The hours a day picture is shown close to as painted. In the Evening
    ## and at Night a place with no picture of its own for the hour is the
    ## day picture under a strong tint, and a row measured on the untinted
    ## picture would leave people daylit in it: those hours keep the general
    ## rows above.
    LIGHT_DAY_HOURS = ("Morning", "Noon", "Afternoon")

    def light_row_ok(row):
        """U0c2. bool: `row` is a light row as a sidecar may hold it: a list
        or tuple of four or six values, "#rrggbb" then plain numbers."""
        if not isinstance(row, (builtins.list, builtins.tuple)) or len(row) not in (4, 6):
            return False
        if not (isinstance(row[0], str) and len(row[0]) == 7 and row[0].startswith("#")):
            return False
        try:
            int(row[0][1:], 16)
        except ValueError:
            return False
        return all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in row[1:])

    def light_row(loc, variant=None):
        """U0c2 (lighting.rpy), final. The measured light of a place's
        picture, a tuple of four or six values, or None: the row
        game/layout/light_<loc>.json holds under `variant` ("evening",
        "night"; None or "" is the day picture), when it is well formed and
        fresh (art_fresh)."""
        key = variant or ""
        row = rule_layout("light_" + str(loc)).get(key)
        if not light_row_ok(row):
            return None
        if not art_fresh("light_%s%s" % (loc, "_" + key if key else ""), art_stem(loc) + ("_" + key if key else "")):
            return None
        return builtins.tuple(row)

    def light_for_place(loc, per):
        v = bg_variant(loc, per)
        ## A measured row for the picture that is showing (U0c2).
        if v or per in LIGHT_DAY_HOURS:
            row = light_row(loc, v)
            if row is not None:
                return row
        if (loc, v) in PLACE_LIGHT:
            return PLACE_LIGHT[(loc, v)]
        if (loc, None) in PLACE_LIGHT:
            return PLACE_LIGHT[(loc, None)]
        indoor = LOCATIONS.get(loc, {}).get("indoor")
        return (INDOOR_LIGHT if indoor else OUTDOOR_LIGHT).get(per, NEUTRAL_LIGHT)

    def light_for_bg(name):
        """A background shown by name: a campus picture keeps its place's
        light (the day picture is daylight), anything else is looked up.
        The second overhaul (U0c2): a measured row comes first, from
        game/layout/light.json for a story picture and from the place's
        own light_<place>.json for a campus picture."""
        row = rule_layout("light").get(name)
        if light_row_ok(row):
            return builtins.tuple(row)
        if name in BG_LIGHT:
            return BG_LIGHT[name]
        parts = name.split()
        base = " ".join(parts[:2])
        variant = parts[2] if len(parts) > 2 else None
        for loc, info in LOCATIONS.items():
            if info["bg"] == base:
                row = light_row(loc, variant)
                if row is not None:
                    return row
                if (loc, variant) in PLACE_LIGHT:
                    return PLACE_LIGHT[(loc, variant)]
                if (loc, None) in PLACE_LIGHT:
                    return PLACE_LIGHT[(loc, None)]
                return NEUTRAL_LIGHT
        ## A story picture's own variant with no row of its own (a district's
        ## night, before its measured row is written) keeps its district's.
        if variant and base in BG_LIGHT:
            return BG_LIGHT[base]
        return NEUTRAL_LIGHT

    ## The scene and show statements go through config.show; watch for
    ## backgrounds going up on the master layer and set the light from them.
    ## A background arrives in one of three shapes:
    ##   ("bg", "city")          scene bg city
    ##   "bg rooftop evening"    scene expression graded_bg(), a painted variant
    ##   "_show_expression_0"    scene expression graded_bg(), a tinted picture;
    ##                           graded_bg() marks those with _light_key, since a
    ##                           character shown with `show expression` looks the same
    _show_unlit = config.show

    def _show_lit(name, *args, **kwargs):
        if kwargs.get("layer") in (None, "master"):
            key = getattr(kwargs.get("what"), "_light_key", None)
            if key:
                store.scene_light = light_for_place(*key)
            elif isinstance(name, tuple) and name and name[0] == "bg":
                store.scene_light = light_for_bg(" ".join(name))
            elif isinstance(name, str) and name.startswith("bg "):
                store.scene_light = light_for_bg(name)
        return _show_unlit(name, *args, **kwargs)

    config.show = _show_lit

    _LIGHT_MATRIX = {}

    def light_matrix(light):
        light = builtins.tuple(light)
        m = _LIGHT_MATRIX.get(light)
        if m is None:
            tint, bright, sat = light[0], light[1], light[2]    # a row of four values, or six
            m = TintMatrix(tint) * SaturationMatrix(sat) * BrightnessMatrix(bright)
            _LIGHT_MATRIX[light] = m
        return m

    def _sprite_light(trans, st, at):
        light = store.scene_light if store.sprite_lighting else NEUTRAL_LIGHT
        trans.matrixcolor = light_matrix(light)
        return 0.25     # keep watching: a background can change under a sprite

    def _shadow_light(trans, st, at):
        light = store.scene_light if store.sprite_lighting else NEUTRAL_LIGHT
        trans.alpha = light[3] if store.sprite_lighting else 0.0
        return 0.25

    ## Plain Transforms rather than ATL `transform` statements, so image
    ## statements can use them whatever order init runs things in.
    def lit(d):
        """A character image, lit by the scene."""
        return Transform(d, function=_sprite_light)

    def lit_sprite(path, size, feet):
        """A generated sprite: lit, with a contact shadow under its feet.

        size is the sprite canvas (w, h); feet is (x centre, sole row, width)
        measured from the neutral pose by tools/gen_sprite_defs.py.

        Phase 2 (D39): when images/char/fx/fx_<who>_blink.png or
        fx_<who>_talk.png exists, the eye box and the mouth box cut from
        them are two more layers over the sprite (view_face_layers,
        view_stage.rpy). Without those files the sprite is built as before.
        """
        fx, fy, fw = feet
        shadow = Transform("images/fx/contact_shadow.png", function=_shadow_light,
                           xysize=(int(fw * 1.6), max(14, int(fw * 0.2))),
                           xcenter=fx, ycenter=fy + 2)
        layers = [shadow, Image(path)] + light_face_layers(path)
        return Transform(Fixed(*layers, xysize=size), function=_sprite_light)

    def light_face_layers(path):
        """P5. The blink and talk layers for a sprite's path ([] when there
        are none). They are view_stage.rpy's; a sprite built before that
        file's init has run gets none."""
        fn = getattr(store, "view_face_layers", None)
        return list(fn(path)) if fn is not None else []

default scene_light = ("#ffffff", 0.0, 1.0, 0.55)
define sprite_lighting = True
