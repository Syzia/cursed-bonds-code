################################################################################
## Cursed Bonds — placeholder backgrounds.
##
## WP0 (phase 1); WP1 tunes them. Each new place borrows an existing picture,
## tinted so it reads as somewhere else. The real art drops in by filename
## with no script change: when images/bg/<name>.png exists it is used instead
## (alley, alley_dark, ridge_veil, utahime_office, gojo_office, map_tokyo,
## shibuya, harajuku, shinjuku, kawasaki, yotsuka, library, the six
## area_<key> pictures of the map's second level, the five hubs:
## school_yard, dorm_yard, staff_yard, training_yard, trailhead, and the new
## places of the second UI overhaul: boys_dorm, yuji_room, megumi_room,
## senpai_room, nobara_room, maki_room, teachers_lounge, teachers_dorm,
## bathhouse, sauna, pool). Their light
## rows are in BG_LIGHT in lighting.rpy (the hubs have none: they are outdoor
## places and take the outdoor light).
##
## The second UI overhaul, U0c2 (docs/UI2_DESIGN.md 5.8, D21, D22):
##
## Nothing lends any more. Five flat pictures used to lend to other names
## through tinted crops: the city at night, the morning street, the town
## street, the ruined hall and the veil. Each was copied, as it stood, to
## images/bg/standin/standin_<name>.png, and every borrower below reads the
## copy (STANDIN_COPIES, standin_copy). So each of those five can be painted
## again at any time and only its own name changes.
##
## Ten more names that always exist, each with its stand-in until
## images/bg/<name>.png is painted: the Sun Mall's three (mall_front,
## mall_hall, mall_atrium), the warehouse, the annexe, and the five kinds of
## board job site (site_tunnel, site_ward, site_platform, site_pool,
## site_karaoke). Each stand-in is the picture that scene plays over today,
## so pointing a scene at its new name changes nothing on screen.
##
## Three names that exist ONLY when their file does: `bg club`,
## `bg shibuya night`, `bg shinjuku night`. night_bg and night_club_bg
## (sb_night.rpy) ask whether the image exists, and fall back to the
## district's own picture while it does not.
##
## The Black Market's ground is a file name, images/bg/market.png, and not an
## image name: its screen draws it when the file exists.
################################################################################

init -3 python:

    def bg_placeholder(path, fallback):
        """WP0. The real picture if it exists (renpy.loadable), else fallback."""
        if renpy.loadable(path):
            return path
        return fallback

    def _bg_tinted(src, matrix, **kw):
        return Transform("images/bg/" + src, matrixcolor=matrix, **kw)

    ## The five flat pictures other names are made from (D22), and where the
    ## copy of each lives. (A copy has a name of its own: two files with one
    ## base name under images/ would give Ren'Py one image name twice.)
    STANDIN_COPIES = ("city_night", "street_morning", "town_street", "ruin_hall", "veil")

    def standin_copy(name):
        """U0c2. The path, from images/bg/, of the copy of a lending picture
        that stand-ins are made from: "standin/standin_<name>.png"."""
        return "standin/standin_%s.png" % name

    def standin_plain(key, lender):
        """U0c2. What `bg <key>` shows for one of the always-defined
        off-campus names: images/bg/<key>.png when it exists, else the copy
        of the picture that scene plays over today, as it is."""
        return bg_placeholder("images/bg/%s.png" % key, "images/bg/" + standin_copy(lender))

    ## name -> the lending picture its stand-in is (5.8). The first five are
    ## the scenes U9 points at them (8.1); the last five are the board's
    ## kinds of job site (sb_board.rpy, BOARD_PLACES).
    STANDIN_NAMES = (
        ("mall_front",    "city_night"),
        ("mall_hall",     "ruin_hall"),
        ("mall_atrium",   "veil"),
        ("warehouse",     "city_night"),
        ("annexe",        "ruin_hall"),
        ("site_tunnel",   "ruin_hall"),
        ("site_ward",     "ruin_hall"),
        ("site_platform", "city_night"),
        ("site_pool",     "veil"),
        ("site_karaoke",  "city_night"),
    )
    for _standin_key, _standin_src in STANDIN_NAMES:
        renpy.image("bg " + _standin_key, standin_plain(_standin_key, _standin_src))
    del _standin_key, _standin_src

    ## image name -> its file, for the three that are defined only when the
    ## file is loadable.
    STANDIN_IF_FILE = (
        ("bg club",           "images/bg/club.png"),
        ("bg shibuya night",  "images/bg/shibuya_night.png"),
        ("bg shinjuku night", "images/bg/shinjuku_night.png"),
    )
    for _standin_name, _standin_file in STANDIN_IF_FILE:
        if renpy.loadable(_standin_file):
            renpy.image(_standin_name, _standin_file)
    del _standin_name, _standin_file

    ## WP1's tuning (task 10): each placeholder borrows a picture that reads
    ## as the right kind of place, cropped or mirrored so it doesn't read as
    ## the place it was borrowed from.

    ## The alley behind the arcade: looking up between the buildings, from
    ## the city at night (not the konbini, which is its own place).
    _ALLEY_CROP = dict(crop=(640, 300, 640, 360), xysize=(1920, 1080))
    renpy.image("bg alley", bg_placeholder("images/bg/alley.png",
        _bg_tinted(standin_copy("city_night"), TintMatrix("#b8c0dc") * SaturationMatrix(0.45) * BrightnessMatrix(-0.12), **_ALLEY_CROP)))

    ## The alley once the lights go out, and the sight opens: nearly every
    ## window gone, and violet.
    renpy.image("bg alley dark", bg_placeholder("images/bg/alley_dark.png",
        _bg_tinted(standin_copy("city_night"), TintMatrix("#a58fe0") * SaturationMatrix(0.35) * BrightnessMatrix(-0.42), **_ALLEY_CROP)))

    ## The veil on the mountain ridge: a dark violet dome over the peak, the
    ## veil picture masked by a soft ellipse (the contact-shadow blob).
    def _veil_dome(cx, cy, w, h):
        mask = Fixed(Transform("images/fx/contact_shadow.png", xysize=(w, h),
                               xpos=cx - w // 2, ypos=cy - h // 2), xysize=(1920, 1080))
        return AlphaMask(_bg_tinted(standin_copy("veil"), TintMatrix("#a080ff") * BrightnessMatrix(0.05)), mask)

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

    ## The Library (phase 2, D34): the classroom, pulled in a little and warmed
    ## like lamplight on old paper. It is still plainly the classroom (the
    ## desks fill the lower half) until images/bg/library.png is painted
    ## (tools/bgs/prompts/library.txt).
    renpy.image("bg library", bg_placeholder("images/bg/library.png",
        _bg_tinted("classroom.png", TintMatrix("#ffdcb0") * SaturationMatrix(0.8) * BrightnessMatrix(-0.05),
                   crop=(120, 60, 1280, 720), xysize=(1920, 1080))))

    ## The Tokyo map: the skyline at night, dimmed under the cards.
    renpy.image("bg map_tokyo", bg_placeholder("images/bg/map_tokyo.png",
        _bg_tinted(standin_copy("city_night"), SaturationMatrix(0.7) * BrightnessMatrix(-0.3))))

    ## The districts. Shibuya: the skyline, pink neon. Shinjuku: the towers
    ## close up, cold. Harajuku: a daytime street (the town street, mirrored
    ## and closer), bright pink. Kawasaki: the low roofs beside the house
    ## in street_morning, cropped so the house is out of frame, bleached.
    ## Yotsuka: home, the street my parents' house is on (street_morning, as
    ## the prologue shows it the morning I leave).
    renpy.image("bg shibuya", bg_placeholder("images/bg/shibuya.png",
        _bg_tinted(standin_copy("city_night"), TintMatrix("#ffbfe6") * BrightnessMatrix(0.02))))
    renpy.image("bg harajuku", bg_placeholder("images/bg/harajuku.png",
        _bg_tinted(standin_copy("town_street"), TintMatrix("#ffc8e4") * SaturationMatrix(1.2) * BrightnessMatrix(0.06),
                   crop=(0, 120, 1280, 720), xysize=(1920, 1080), xzoom=-1.0)))
    renpy.image("bg shinjuku", bg_placeholder("images/bg/shinjuku.png",
        _bg_tinted(standin_copy("city_night"), TintMatrix("#b4ecff") * BrightnessMatrix(-0.06),
                   crop=(760, 160, 960, 540), xysize=(1920, 1080))))
    renpy.image("bg kawasaki", bg_placeholder("images/bg/kawasaki.png",
        _bg_tinted(standin_copy("street_morning"), TintMatrix("#ece6da") * SaturationMatrix(0.5) * BrightnessMatrix(0.03),
                   crop=(1180, 130, 740, 416), xysize=(1920, 1080))))
    renpy.image("bg yotsuka", bg_placeholder("images/bg/yotsuka.png",
        _bg_tinted(standin_copy("street_morning"), TintMatrix("#ffe4c4"))))


## The six area pictures of the map's second level (phase 2, 4.1): the painted
## images/bg/area_<key>.png, or until it exists a piece of map_campus.png
## around the area's anchor, clamped to the picture, enlarged and darkened
## (world_area_bg in sb_world.rpy, which knows the anchors; this block runs
## after it).
init -1 python:

    renpy.image("bg area_heart", world_area_bg("heart"))
    renpy.image("bg area_school", world_area_bg("school"))
    renpy.image("bg area_dorms", world_area_bg("dorms"))
    renpy.image("bg area_staff", world_area_bg("staff"))
    renpy.image("bg area_grounds", world_area_bg("grounds"))
    renpy.image("bg area_mountain", world_area_bg("mountain"))

    ## The five hubs (phase 2, D53 and D58): the outdoor place each area's
    ## rooms open onto. images/bg/<name>.png when it is painted
    ## (tools/bgs/prompts/<name>.txt), else a stand-in borrowed from the
    ## courtyard or the forest trail (world_hub_bg in sb_world.rpy, which
    ## holds the table: WORLD_HUB_STANDINS).
    renpy.image("bg school_yard", world_hub_bg("school_yard"))
    renpy.image("bg dorm_yard", world_hub_bg("dorm_yard"))
    renpy.image("bg staff_yard", world_hub_bg("staff_yard"))
    renpy.image("bg training_yard", world_hub_bg("training_yard"))
    renpy.image("bg trailhead", world_hub_bg("trailhead"))

    ## The second UI overhaul (docs/UI2_DESIGN.md 4.1, K12; U0b): a new place
    ## is walkable on a stand-in before its picture exists. Each stand-in is a
    ## picture the game already has, mirrored and tinted so that it cannot be
    ## mistaken for the real room; images/bg/<key>.png replaces it at the next
    ## launch with no script change. While config.developer is on, a small
    ## "stand-in" tag sits near the bottom left corner (above the review
    ## tools' button, which the same switch shows).
    def standin_bg(key, src, matrix, **kw):
        """U0b. What `bg <key>` shows: images/bg/<key>.png when it exists,
        else the stand-in: images/bg/<src> under `matrix` (and any crop or
        mirror in kw), with the developer's "stand-in" tag."""
        tag = ConditionSwitch(
            "config.developer", Text("stand-in", size=16, color="#ffffffb0", outlines=[(1, "#000000b0", 0, 0)]),
            "True", Null())
        return bg_placeholder("images/bg/%s.png" % key,
            Fixed(_bg_tinted(src, matrix, **kw),
                  Transform(tag, xpos=40, ypos=1014),
                  xysize=(1920, 1080)))

    ## The Boys' Dormitory: the girls' corridor, mirrored, in cool grey.
    renpy.image("bg boys_dorm", standin_bg("boys_dorm", "girls_dorm.png",
        TintMatrix("#d6dde8") * SaturationMatrix(0.45) * BrightnessMatrix(-0.02), xzoom=-1.0))
    ## The three friends' rooms: my room, mirrored, in three tints (warm for
    ## Yuji, blue for Megumi, green for the room Panda and Toge share).
    renpy.image("bg yuji_room", standin_bg("yuji_room", "your_room.png",
        TintMatrix("#ffd9b0") * SaturationMatrix(0.85), xzoom=-1.0))
    renpy.image("bg megumi_room", standin_bg("megumi_room", "your_room.png",
        TintMatrix("#b9cdf2") * SaturationMatrix(0.70) * BrightnessMatrix(-0.02), xzoom=-1.0))
    renpy.image("bg senpai_room", standin_bg("senpai_room", "your_room.png",
        TintMatrix("#c4e6c0") * SaturationMatrix(0.80), xzoom=-1.0))

    ## U0c1: the other seven places (4.1's table of stand-ins). Nobody is in
    ## any of these pictures (K16).
    ## The two girls' rooms: my room, not mirrored, in rose and in slate.
    renpy.image("bg nobara_room", standin_bg("nobara_room", "your_room.png",
        TintMatrix("#ffc4d6") * SaturationMatrix(0.80)))
    renpy.image("bg maki_room", standin_bg("maki_room", "your_room.png",
        TintMatrix("#b4bcc8") * SaturationMatrix(0.40) * BrightnessMatrix(-0.03)))
    ## The Teachers' Lounge: the Common Room, in violet-grey.
    renpy.image("bg teachers_lounge", standin_bg("teachers_lounge", "dorm_common.png",
        TintMatrix("#cfc6e2") * SaturationMatrix(0.45) * BrightnessMatrix(-0.02)))
    ## The Teachers' Dormitory: the Principal's Office, cropped, warm, and
    ## lifted: the office is painted by candlelight, and under the Night's
    ## grade it went almost black (Yaga is met here at Night).
    renpy.image("bg teachers_dorm", standin_bg("teachers_dorm", "office.png",
        TintMatrix("#ffd9a8") * BrightnessMatrix(0.18), crop=(320, 180, 1280, 720), xysize=(1920, 1080)))
    ## The Onsen's rest hall: the infirmary, in pale teal.
    renpy.image("bg bathhouse", standin_bg("bathhouse", "infirmary.png",
        TintMatrix("#c4f0ea") * SaturationMatrix(0.60) * BrightnessMatrix(0.04)))
    ## The Sauna: the storehouse, in amber.
    renpy.image("bg sauna", standin_bg("sauna", "storehouse.png",
        TintMatrix("#ffc070") * SaturationMatrix(0.70) * BrightnessMatrix(0.04)))
    ## The Swimming Pool: the riverside, cropped to the water, in cyan.
    renpy.image("bg pool", standin_bg("pool", "riverside.png",
        TintMatrix("#a8ecff") * SaturationMatrix(0.85), crop=(640, 500, 960, 540), xysize=(1920, 1080)))
