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
    }

    def light_for_place(loc, per):
        v = bg_variant(loc, per)
        if (loc, v) in PLACE_LIGHT:
            return PLACE_LIGHT[(loc, v)]
        if (loc, None) in PLACE_LIGHT:
            return PLACE_LIGHT[(loc, None)]
        indoor = LOCATIONS.get(loc, {}).get("indoor")
        return (INDOOR_LIGHT if indoor else OUTDOOR_LIGHT).get(per, NEUTRAL_LIGHT)

    def light_for_bg(name):
        """A background shown by name: a campus picture keeps its place's
        light (the day picture is daylight), anything else is looked up."""
        if name in BG_LIGHT:
            return BG_LIGHT[name]
        parts = name.split()
        base = " ".join(parts[:2])
        variant = parts[2] if len(parts) > 2 else None
        for loc, info in LOCATIONS.items():
            if info["bg"] == base:
                if (loc, variant) in PLACE_LIGHT:
                    return PLACE_LIGHT[(loc, variant)]
                if (loc, None) in PLACE_LIGHT:
                    return PLACE_LIGHT[(loc, None)]
                return NEUTRAL_LIGHT
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
        m = _LIGHT_MATRIX.get(light)
        if m is None:
            tint, bright, sat, _ = light
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
        """
        fx, fy, fw = feet
        shadow = Transform("images/fx/contact_shadow.png", function=_shadow_light,
                           xysize=(int(fw * 1.6), max(14, int(fw * 0.2))),
                           xcenter=fx, ycenter=fy + 2)
        return Transform(Fixed(shadow, Image(path), xysize=size), function=_sprite_light)

default scene_light = ("#ffffff", 0.0, 1.0, 0.55)
define sprite_lighting = True
