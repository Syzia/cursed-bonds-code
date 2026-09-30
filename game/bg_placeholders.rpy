################################################################################
## Cursed Bonds — placeholder backgrounds.
##
## WP0 (phase 1); WP1 tunes them. Each new place borrows an existing picture,
## tinted so it reads as somewhere else. The real art drops in by filename
## with no script change: when images/bg/<name>.png exists it is used instead
## (alley, alley_dark, ridge_veil, utahime_office, gojo_office, map_tokyo,
## shibuya, harajuku, shinjuku, kawasaki, yotsuka). Their light rows are in
## BG_LIGHT in lighting.rpy.
################################################################################

init -3 python:

    def bg_placeholder(path, fallback):
        """WP0. The real picture if it exists (renpy.loadable), else fallback."""
        if renpy.loadable(path):
            return path
        return fallback

    def _bg_tinted(src, matrix, **kw):
        return Transform("images/bg/" + src, matrixcolor=matrix, **kw)

    ## WP1's tuning (task 10): each placeholder borrows a picture that reads
    ## as the right kind of place, cropped or mirrored so it doesn't read as
    ## the place it was borrowed from.

    ## The alley behind the arcade: looking up between the buildings, from
    ## the city at night (not the konbini, which is its own place).
    _ALLEY_CROP = dict(crop=(640, 300, 640, 360), xysize=(1920, 1080))
    renpy.image("bg alley", bg_placeholder("images/bg/alley.png",
        _bg_tinted("city_night.png", TintMatrix("#b8c0dc") * SaturationMatrix(0.45) * BrightnessMatrix(-0.12), **_ALLEY_CROP)))

    ## The alley once the lights go out, and the sight opens: nearly every
    ## window gone, and violet.
    renpy.image("bg alley dark", bg_placeholder("images/bg/alley_dark.png",
        _bg_tinted("city_night.png", TintMatrix("#a58fe0") * SaturationMatrix(0.35) * BrightnessMatrix(-0.42), **_ALLEY_CROP)))

    ## The veil on the mountain ridge: a dark violet dome over the peak, the
    ## veil picture masked by a soft ellipse (the contact-shadow blob).
    def _veil_dome(cx, cy, w, h):
        mask = Fixed(Transform("images/fx/contact_shadow.png", xysize=(w, h),
                               xpos=cx - w // 2, ypos=cy - h // 2), xysize=(1920, 1080))
        return AlphaMask(Transform("images/bg/veil.png", matrixcolor=TintMatrix("#a080ff") * BrightnessMatrix(0.05)), mask)

    renpy.image("bg ridge_veil", bg_placeholder("images/bg/ridge_veil.png",
        Composite((1920, 1080),
                  (0, 0), _bg_tinted("ridge.png", TintMatrix("#cfc6ec") * SaturationMatrix(0.75) * BrightnessMatrix(-0.12)),
                  (0, 0), _veil_dome(1170, 380, 1100, 760))))

    ## The two new offices. Utahime's: the dojo's tall windows, cropped, in
    ## cool daylight (neat, traditional). Gojo's: the common room mirrored
    ## and warmed pink (a sofa and a very large television).
    renpy.image("bg utahime_office", bg_placeholder("images/bg/utahime_office.png",
        _bg_tinted("dojo.png", TintMatrix("#dfe6ff"), crop=(0, 40, 1120, 630), xysize=(1920, 1080))))
    renpy.image("bg gojo_office", bg_placeholder("images/bg/gojo_office.png",
        _bg_tinted("dorm_common.png", TintMatrix("#ffd2e2") * BrightnessMatrix(0.03), xzoom=-1.0)))

    ## The Tokyo map: the skyline at night, dimmed under the cards.
    renpy.image("bg map_tokyo", bg_placeholder("images/bg/map_tokyo.png",
        _bg_tinted("city_night.png", SaturationMatrix(0.7) * BrightnessMatrix(-0.3))))

    ## The districts. Shibuya: the skyline, pink neon. Shinjuku: the towers
    ## close up, cold. Harajuku: a shopfront (the konbini) in bright pink
    ## daylight. Kawasaki: low roofs, bleached. Yotsuka: the street at home.
    renpy.image("bg shibuya", bg_placeholder("images/bg/shibuya.png",
        _bg_tinted("city_night.png", TintMatrix("#ffbfe6") * BrightnessMatrix(0.02))))
    renpy.image("bg harajuku", bg_placeholder("images/bg/harajuku.png",
        _bg_tinted("konbini.png", TintMatrix("#ffd6ea") * BrightnessMatrix(0.10), xzoom=-1.0)))
    renpy.image("bg shinjuku", bg_placeholder("images/bg/shinjuku.png",
        _bg_tinted("city_night.png", TintMatrix("#b4ecff") * BrightnessMatrix(-0.06),
                   crop=(760, 160, 960, 540), xysize=(1920, 1080))))
    renpy.image("bg kawasaki", bg_placeholder("images/bg/kawasaki.png",
        _bg_tinted("town_street.png", TintMatrix("#e6e2da") * SaturationMatrix(0.7) * BrightnessMatrix(-0.04))))
    renpy.image("bg yotsuka", bg_placeholder("images/bg/yotsuka.png",
        _bg_tinted("street_morning.png", TintMatrix("#ffe4c4"))))
