################################################################################
## Cursed Bonds — cursed energy and Last Light.
##
## WP2 owns this file (PHASE1_DESIGN.md 3.4). There is one technique, Last
## Light (残光, Zankō): the instant the lights went out, held still. Its
## internal key stays "timestop" for ever, and tech() returns it whatever an
## old save's `technique` holds (migration 10 in sb_grades.rpy rewrites that
## value on load).
##
## Stat growth is capped by the player's grade (grade_cap in sb_grades.rpy):
## gain() stops control and output at the cap, never lowers a value already
## above it, and says so once a day per stat.
################################################################################

init -2 python:
    import builtins

    ## Last Light ---------------------------------------------------------------
    ##
    ## Its sandbox verb is Hold: once a day the hour does not pass.

    class _TechniqueTable(builtins.dict):
        """WP2. TECHNIQUES holds only "timestop". Any other key (an old save's
        technique, read by a scene not yet converted) gets Last Light too,
        instead of a KeyError. Init-time data: never saved."""

        def __missing__(self, key):
            return builtins.dict.__getitem__(self, "timestop")

    TECHNIQUES = _TechniqueTable(
        timestop=dict(
            name="Last Light",
            jp="残光 · Zankō",
            tag="Control",
            scales="control",
            blurb=("I hold the instant the lights went out. It is not speed and it is not "
                   "foresight: the second simply does not happen until I let it."),
            verb="Hold",
            verb_desc="Once a day, spend most of my reserve and the hour does not pass.",
            tiers=[
                ("Stutter", "A held half-second. Enough to be somewhere else.", 0),
                ("Held Second", "A full second, and I can move inside it.", 30),
                ("Arrest", "Long enough to walk across a room nobody is crossing.", 60),
                ("The Second That Did Not Happen", "Domain Expansion.", 90),
            ],
        ),
    )

    def tech():
        """WP2. The player's technique: always Last Light, whatever
        store.technique holds."""
        return TECHNIQUES["timestop"]

    def tech_stat():
        """WP2. The value of the stat Last Light scales off (control)."""
        return getattr(store, tech()["scales"])

    def tech_tier():
        """WP2. (index, name, description) of the highest unlocked tier."""
        t = tech()
        stat = tech_stat()
        idx = 0
        for i, (nm, desc, req) in enumerate(t["tiers"]):
            if stat >= req:
                idx = i
        nm, desc, req = t["tiers"][idx]
        return idx, nm, desc

    def next_tier():
        """WP2. (name, requirement) of the next locked tier, or None."""
        t = tech()
        stat = tech_stat()
        for nm, desc, req in t["tiers"]:
            if stat < req:
                return nm, req
        return None

    ## Energy -------------------------------------------------------------------

    def spend_ce(amount):
        """WP2. Spend reserve. Returns False (and spends nothing) if I can't afford it."""
        if store.ce < amount:
            return False
        store.ce -= amount
        renpy.restart_interaction()
        return True

    def restore_ce(amount):
        """WP2. Refill reserve, up to ce_max."""
        store.ce = min(store.ce_max, store.ce + amount)

    def spend_stamina(amount):
        """WP2. Spend stamina, down to 0."""
        store.stamina = max(0, store.stamina - amount)

    ## The stats a grade caps; insight only ever stops at 100.
    GRADE_CAPPED_STATS = ("control", "output")

    def gain(stat, amount, quiet=False):
        """WP2. Raise (or, with a negative amount, lower) control, output or
        insight.

        Diminishing returns from 60 and from 85, as before. Control and output
        stop at the grade's stat cap (grade_cap("stat"), Grade 4's while
        unassessed); a value already above it is never lowered, and once a day
        per stat a toast says a promotion lifts it ("cap:<stat>" in
        actions_today). Insight stops at 100. Toasts use kind "stat"; quiet
        silences the gain and the cap toasts, not a tier advance."""
        cur = getattr(store, stat)
        if amount > 0:
            if cur >= 60:
                amount = max(1, int(amount * 0.6))
            if cur >= 85:
                amount = max(1, int(amount * 0.5))
        cap = 100
        if stat in GRADE_CAPPED_STATS:
            cap = grade_cap("stat")
            if cap is None:
                cap = 100
        before_tier = tech_tier()[0]
        capped = False
        if amount > 0:
            new = min(cur + amount, max(cur, cap))
            capped = cur + amount > cap
        else:
            new = max(0, cur + amount)
        setattr(store, stat, new)
        if not quiet and new != cur:
            toast("%s %+d" % (stat.capitalize(), new - cur), "stat", None, new - cur)
        if capped and not quiet and stat in GRADE_CAPPED_STATS:
            key = "cap:" + stat
            if key not in store.actions_today:
                store.actions_today.add(key)
                toast("%s is at the %s limit — a promotion lifts it"
                      % (stat.capitalize(), grade_label(grade_key(store.grade) or "g4")), "stat")
        if tech_tier()[0] > before_tier:
            toast("Technique advanced — %s" % tech_tier()[1], "stat")

    def add_ce(amount):
        """WP2. Prologue-era shim: raise the stat Last Light scales off."""
        gain(tech()["scales"], amount, quiet=(amount < 0))

    def grade_name():
        """WP2. The player's grade in words ("Grade 4", or "Not yet assessed")."""
        return grade_label(store.grade)


## Stats ########################################################################

default technique = "timestop"

default ce      = 60      # spendable reserve
default ce_max  = 60
default control = 12      # precision, technique shaping
default output  = 10      # raw destructive force
default insight = 10      # reading cursed energy, people, rooms
default grade   = None    # a GRADES key from roll call on (D16); None = not yet assessed
