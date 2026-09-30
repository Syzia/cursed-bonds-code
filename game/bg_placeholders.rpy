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

    def _bg_tinted(src, matrix):
        return Transform("images/bg/" + src, matrixcolor=matrix)

    ## The alley behind the arcade: the konbini picture, darker and greyer.
    renpy.image("bg alley", bg_placeholder("images/bg/alley.png",
        _bg_tinted("konbini.png", SaturationMatrix(0.6) * BrightnessMatrix(-0.25))))

    ## The alley once the lights go out, and the sight opens.
    renpy.image("bg alley dark", bg_placeholder("images/bg/alley_dark.png",
        _bg_tinted("konbini.png", TintMatrix("#a58fe0") * SaturationMatrix(0.5) * BrightnessMatrix(-0.45))))

    ## The veil on the mountain ridge.
    renpy.image("bg ridge_veil", bg_placeholder("images/bg/ridge_veil.png",
        Composite((1920, 1080),
                  (0, 0), "images/bg/ridge.png",
                  (0, 0), Transform("images/bg/veil.png", alpha=0.35))))

    ## The two new offices.
    renpy.image("bg utahime_office", bg_placeholder("images/bg/utahime_office.png",
        _bg_tinted("office.png", TintMatrix("#c9d8ff") * BrightnessMatrix(0.02))))
    renpy.image("bg gojo_office", bg_placeholder("images/bg/gojo_office.png",
        _bg_tinted("dorm_common.png", TintMatrix("#ffd2e2") * BrightnessMatrix(0.03))))

    ## The Tokyo map.
    renpy.image("bg map_tokyo", bg_placeholder("images/bg/map_tokyo.png",
        _bg_tinted("city_night.png", BrightnessMatrix(-0.5))))

    ## The districts.
    renpy.image("bg shibuya", bg_placeholder("images/bg/shibuya.png",
        _bg_tinted("city_night.png", TintMatrix("#ffbfe6") * BrightnessMatrix(0.02))))
    renpy.image("bg harajuku", bg_placeholder("images/bg/harajuku.png",
        _bg_tinted("street_morning.png", TintMatrix("#ffdcea") * BrightnessMatrix(0.03))))
    renpy.image("bg shinjuku", bg_placeholder("images/bg/shinjuku.png",
        _bg_tinted("city_night.png", TintMatrix("#b4ecff") * BrightnessMatrix(-0.08))))
    renpy.image("bg kawasaki", bg_placeholder("images/bg/kawasaki.png",
        _bg_tinted("town_street.png", TintMatrix("#e6e2da") * SaturationMatrix(0.7) * BrightnessMatrix(-0.04))))
    renpy.image("bg yotsuka", bg_placeholder("images/bg/yotsuka.png",
        _bg_tinted("town_street.png", TintMatrix("#ffe4c4"))))
