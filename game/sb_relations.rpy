################################################################################
## Cursed Bonds — bonds, affection, and the roster.
################################################################################

init -2 python:

    ROSTER_ORDER = ["yuji", "megumi", "nobara", "maki", "panda", "toge",
                    "shoko", "gojo", "yaga"]

    ## romance=True means an Affection track exists alongside Bond.
    CAST = {
        "yuji": dict(name="Yuji Itadori", short="Yuji", color="#ff8fa3", romance=False,
                     year="1st year",
                     blurb="Vessel of Sukuna. Punches first, worries about it later."),
        "megumi": dict(name="Megumi Fushiguro", short="Megumi", color="#8fb0ff", romance=False,
                       year="1st year",
                       blurb="Ten Shadows. Says four words when one would do."),
        "nobara": dict(name="Nobara Kugisaki", short="Nobara", color="#ffb066", romance=True,
                       year="1st year",
                       blurb="Straw Doll Technique. Absolutely will not be pitied."),
        "maki": dict(name="Maki Zenin", short="Maki", color="#77e0a0", romance=True,
                     year="2nd year",
                     blurb="No cursed energy, all cursed tools. Do not go easy on her."),
        "panda": dict(name="Panda", short="Panda", color="#e6e6f0", romance=False,
                      year="2nd year",
                      blurb="Cursed corpse. The most emotionally literate person here."),
        "toge": dict(name="Toge Inumaki", short="Toge", color="#bfe3ea", romance=False,
                     year="2nd year",
                     blurb="Cursed Speech. Speaks in rice-ball ingredients to keep you alive."),
        "shoko": dict(name="Shoko Ieiri", short="Shoko", color="#e0c8b0", romance=True,
                      year="Doctor",
                      blurb="Reverse Cursed Technique. Has seen worse. Has seen all of it."),
        "gojo": dict(name="Satoru Gojo", short="Gojo", color="#8ed6ff", romance=False,
                     year="Teacher",
                     blurb="The strongest. Deeply unserious about it."),
        "yaga": dict(name="Masamichi Yaga", short="Yaga", color="#b0b8c8", romance=False,
                     year="Principal",
                     blurb="Principal. Builds cursed corpses. Does not build excuses."),
    }

    BOND_RANKS = [(0, "Stranger"), (20, "Acquaintance"), (40, "Comrade"),
                  (60, "Trusted"), (80, "Sworn"), (100, "Unbreakable")]

    ## Affection past 100 only exists after the confession scene, which is why
    ## the second half of this table is unreachable until then.
    AFF_RANKS = [(0, "—"), (20, "Warm"), (40, "Close"),
                 (60, "Something There"), (80, "Falling"), (100, "Yours"),
                 (125, "Certain"), (150, "Devoted"), (175, "Inseparable"),
                 (200, "Unconditional")]

    AFF_BASE_MAX = 100      # ceiling before the confession
    AFF_TRUE_MAX = 200      # ceiling after it

    ## Affection cannot outrun friendship. This is the gate that makes romance
    ## something you earn rather than something you grind.
    AFF_CAP_BY_BOND = [(0, 0), (30, 20), (50, 40), (70, 70), (85, 100)]

    def rank_of(table, value):
        idx = 0
        for i, (threshold, nm) in enumerate(table):
            if value >= threshold:
                idx = i
        return idx, table[idx][1]

    def bond_rank(v):
        return rank_of(BOND_RANKS, v)

    def aff_rank(v):
        return rank_of(AFF_RANKS, v)

    def is_romanceable(who):
        return CAST.get(who, {}).get("romance", False)

    def is_together(who):
        """True once the confession scene has been played with this person."""
        return who in store.together

    def aff_cap(who):
        """Bond gates affection up to 100. The confession lifts the lid to 200."""
        if is_together(who):
            return AFF_TRUE_MAX
        b = store.bonds.get(who, 0)
        cap = 0
        for need_bond, allowed in AFF_CAP_BY_BOND:
            if b >= need_bond:
                cap = allowed
        return cap

    def confession_ready(who):
        """Affection is maxed out and there is nowhere left for it to go."""
        return (is_romanceable(who) and not is_together(who)
                and store.affection.get(who, 0) >= AFF_BASE_MAX)

    def begin_together(who):
        store.together.append(who)
        flag("together_" + who)
        renpy.notify("%s — together" % CAST[who]["short"])

    def add_bond(who, amount, quiet=False):
        before = store.bonds.get(who, 0)
        after = max(0, min(100, before + amount))
        store.bonds[who] = after
        if quiet or after == before:
            return
        renpy.notify("%s  bond %+d" % (CAST[who]["short"], after - before))
        if bond_rank(after)[0] > bond_rank(before)[0]:
            renpy.notify("%s — %s" % (CAST[who]["short"], bond_rank(after)[1]))

    def add_aff(who, amount, quiet=False):
        """Affection is capped by bond; overflow is silently discarded."""
        if not is_romanceable(who):
            return add_bond(who, amount, quiet)
        before = store.affection.get(who, 0)
        cap = aff_cap(who)
        after = max(0, min(cap, before + amount))
        store.affection[who] = after
        if quiet or after == before:
            if amount > 0 and before >= cap and not quiet:
                renpy.notify("%s — you'd have to know them better first." % CAST[who]["short"])
            return
        renpy.notify("%s  ♡ %+d" % (CAST[who]["short"], after - before))
        if aff_rank(after)[0] > aff_rank(before)[0]:
            renpy.notify("%s — %s" % (CAST[who]["short"], aff_rank(after)[1]))

    def recruit(who):
        """Add someone to the roster. They start appearing on the map."""
        if who in store.roster:
            return
        store.roster.append(who)
        store.bonds.setdefault(who, 0)
        if is_romanceable(who):
            store.affection.setdefault(who, 0)
        renpy.notify("%s joined your circle." % CAST[who]["name"])

    def partner():
        """Whoever you are actually closest to, romance first."""
        best, score = None, -1
        for c in store.roster:
            s = store.bonds.get(c, 0) + store.affection.get(c, 0) * 1.5
            if s > score:
                best, score = c, s
        return best

    ## Aliases kept so the prologue and the summary screen keep working.
    BOND_ORDER = ROSTER_ORDER

    def bond_value(who):
        return store.bonds.get(who, 0)

    def total_bond():
        return sum(store.bonds.values())

    def closest_first_year():
        firsts = ["yuji", "megumi", "nobara"]
        return max(firsts, key=lambda k: (store.bonds.get(k, 0), -firsts.index(k)))

    def flag(name):
        store.flags.add(name)

    def has_flag(name):
        return name in store.flags


## Relationship state ###########################################################

default roster    = ["yuji", "megumi", "nobara", "maki", "panda", "toge", "shoko", "gojo", "yaga"]
default bonds     = {}
default affection = {}
default flags     = set()
default together  = []
default arc       = 1
