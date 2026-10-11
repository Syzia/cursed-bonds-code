################################################################################
## Cursed Bonds — the record of which picture is at which revision.
##
## The second UI overhaul, U0c2 (docs/UI2_DESIGN.md 5.5, K7, D20). Final:
## frozen after wave 0.
##
## game/layout/pictures.json is written only by the install tools and read
## here, once. It is init data and is never saved. A picture with no row is
## today's picture (revision 1), and with no file at all the game behaves
## exactly as it did before the file existed.
##
##   {"pictures": {
##     "courtyard":           {"rev": 2, "kind": "composed", ...},
##     "dorm_common":         {"rev": 3, "kind": "inplace", ...},
##     "dorm_common_evening": {"rev": 2, "kind": "relight", "of": "dorm_common", "of_rev": 3},
##     "library_lit":         {"rev": 2, "kind": "relight", "of": "library", "of_rev": 2},
##     "fg_dorm_common":      {"of": "dorm_common", "of_rev": 3},
##     "light_dorm_common":   {"of": "dorm_common", "of_rev": 3},
##     "pose_dorm_common__nobara__evening": {"of": "dorm_common_evening", "of_rev": 2}
##   }}
##
## A key is a picture's file stem ("your_room" for My Room, K1), or the name
## of something made from a picture: fg_<place>[_<hour>], light_<place>[_<hour>],
## pose_<place>__<who>[__<variant>][__asleep], where <place> is the place's
## key ("dorm") and its row names the picture it was made from (`of`) and
## that picture's revision at the time (`of_rev`).
##
##   art_rev(stem)          the picture's revision; 1 when it has no row
##   art_fresh(stem)        False when what `stem` was made from has moved on
##   art_stem(loc)          a place's picture stem ("dorm" -> "your_room")
##   art_validate()         lint: the rows' shapes
##
## The four gates that read these (K7: nothing stale is shown) are in the
## files that own what they guard: bg_variant (sb_world.rpy), view_fg_path
## and view_pose (view_stage.rpy), light_for_place (lighting.rpy).
################################################################################

init -6 python:
    import builtins as art_builtins
    import json as art_json

    ## The hour pictures a place may have: the attribute, which is also the
    ## end of the file's stem ("rooftop_evening"). U0n (5.7a, D61): "lit" is
    ## the room at Night with someone up in it ("library_lit"), a second
    ## Night picture beside "night", the room with nobody up. It is read to
    ## its parent as an hour's name is: fg_<place>_lit, light_<place>_lit and
    ## pose_<place>__<who>__lit are made from <picture>_lit, and that from
    ## the day picture.
    ART_HOURS = ("evening", "night", "lit")

    ## The manifest's rows, read once: {stem: row}. Outside the store, and
    ## never reassigned: it is not saved and rollback leaves it alone. (A
    ## harness may change its rows in place to test a gate.)
    ART_PICTURES = art_builtins.dict()
    ART_READ = art_builtins.list([False])

    def art_rows():
        """U0c2. {stem: row}: the rows of game/layout/pictures.json, read
        once; {} when there is no file, or it does not hold
        {"pictures": {...}}."""
        if not ART_READ[0]:
            ART_READ[0] = True
            path = "layout/pictures.json"
            if renpy.loadable(path):
                try:
                    with renpy.open_file(path, encoding="utf-8") as f:
                        got = art_json.load(f)
                    rows = got.get("pictures") if isinstance(got, art_builtins.dict) else None
                    if isinstance(rows, art_builtins.dict):
                        for k, r in rows.items():
                            if isinstance(r, art_builtins.dict):
                                ART_PICTURES[str(k)] = r
                except Exception:
                    if config.developer:
                        raise
        return ART_PICTURES

    def art_int(v):
        """U0c2. bool: v is a whole number, 1 or more (a revision)."""
        return isinstance(v, int) and not isinstance(v, bool) and v >= 1

    def art_rev(stem):
        """U0c2 (art_manifest.rpy), final. int: the revision of the picture
        with this file stem ("courtyard", "your_room", "dorm_common_evening");
        1 when the manifest has no row for it (today's picture)."""
        row = art_rows().get(str(stem))
        if row is not None and art_int(row.get("rev")):
            return row["rev"]
        return 1

    def art_stem(loc):
        """U0c2. The file stem of a place's picture, from its image name
        (LOCATIONS[loc]["bg"]): "courtyard" for the Courtyard, "your_room"
        for My Room (K1). The key itself for anything that is not a place."""
        info = getattr(store, "LOCATIONS", {}).get(loc)
        if info:
            parts = str(info.get("bg", "")).split()
            if len(parts) >= 2:
                return parts[1]
        return str(loc)

    def art_parent(stem):
        """U0c2. The stem of the picture `stem` was made from, read from its
        name, or None for a picture that was made from no other (a day
        picture, a map, a story picture):

          <picture>_evening, <picture>_night, <picture>_lit
                                                 the day picture
          fg_<place>[_<hour>]                    the place's picture for that hour
          light_<place>[_<hour>]                 the same
          pose_<place>__<who>[__<variant>][__asleep]
                                                 the place's picture for the variant
        """
        stem = str(stem)
        places = getattr(store, "LOCATIONS", {})
        for head in ("fg_", "light_"):
            if stem.startswith(head):
                rest = stem[len(head):]
                if rest in places:
                    return art_stem(rest)
                for hour in ART_HOURS:
                    if rest.endswith("_" + hour) and rest[:-len(hour) - 1] in places:
                        return "%s_%s" % (art_stem(rest[:-len(hour) - 1]), hour)
                return None
        if stem.startswith("pose_"):
            parts = stem[len("pose_"):].split("__")
            if len(parts) < 2:
                return None
            variant = [p for p in parts[2:] if p in ART_HOURS]
            return art_stem(parts[0]) + ("_" + variant[0] if variant else "")
        stems = art_builtins.set(art_stem(l) for l in places)
        for hour in ART_HOURS:
            if stem.endswith("_" + hour) and stem[:-len(hour) - 1] in stems:
                return stem[:-len(hour) - 1]
        return None

    def art_fresh(stem, of=None, depth=0):
        """U0c2 (art_manifest.rpy), final. bool: what `stem` names is still
        the one made for the picture it was made from (K7).

        With a row that names a parent (`of`): False when the parent's
        revision is no longer the row's `of_rev`. With no row: fresh only
        while its parent is at revision 1 (it was made for today's picture).
        The parent of a thing with no row is `of` when given, else read from
        its name (art_parent); a picture made from no other is always fresh.
        Something whose parent is itself stale is stale too."""
        stem = str(stem)
        row = art_rows().get(stem)
        if row is not None and row.get("of"):
            parent = str(row["of"])
            if art_rev(parent) != row.get("of_rev"):
                return False
        else:
            parent = of or art_parent(stem)
            if not parent:
                return True
            if art_rev(parent) != 1:
                return False
        if depth < 4 and parent != stem:
            return art_fresh(parent, None, depth + 1)
        return True

    def art_validate():
        """U0c2. Lint findings for the manifest: each row's shape. A row that
        has gone stale is not a finding: the game steps round it (the four
        gates) and tools/art_status.py lists it, since that is the ordinary
        state between two art batches."""
        out = []
        rows = art_rows()
        for stem in art_builtins.sorted(rows):
            r = rows[stem]
            if "rev" in r and not art_int(r["rev"]):
                out.append("pictures.json %r: rev must be a whole number, 1 or more" % (stem,))
            if ("of" in r) != ("of_rev" in r) or ("of" in r and not (isinstance(r["of"], str) and art_int(r["of_rev"]))):
                out.append("pictures.json %r: `of` (a file stem) and `of_rev` (its revision) go together" % (stem,))
                continue
            if "rev" not in r and "of" not in r:
                out.append("pictures.json %r: a row holds `rev`, or `of` and `of_rev`" % (stem,))
        return out


init python:
    register_validator(art_validate)
