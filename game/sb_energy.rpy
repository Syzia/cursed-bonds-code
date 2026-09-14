################################################################################
## Cursed Bonds — cursed energy and innate techniques.
################################################################################

init -2 python:

    ## Techniques ---------------------------------------------------------------
    ##
    ## Each one has a *sandbox verb* — something it lets you do while walking
    ## around the campus, not just something it does in a fight. That is the
    ## whole point of picking one.

    TECHNIQUES = {
        "filament": dict(
            name="Filament",
            jp="Shibaku — Thread-Bind",
            tag="Control",
            scales="control",
            blurb=("You spin cursed energy into threads finer than hair. They cut, "
                   "they bind, and they report back what they touch."),
            verb="Sense",
            verb_desc=("Cast threads across the campus. You can see where everyone is "
                       "from the map, without walking there."),
            tiers=[
                ("Filament",   "Threads that cut and read a room.", 0),
                ("Suture",     "Stitch a wound closed — yours or someone else's.", 30),
                ("Marionette", "Move something that is not your body.", 60),
                ("Loom of Ten Thousand Ends", "Domain Expansion.", 90),
            ],
        ),
        "emberfall": dict(
            name="Emberfall",
            jp="Zanka — Lingering Fire",
            tag="Output",
            scales="output",
            blurb=("Your cursed energy burns slow and stays where you put it. "
                   "Anything you strike keeps cooking long after you walk away."),
            verb="Temper",
            verb_desc=("Work the storehouse forge. Temper cursed tools for yourself "
                       "and for anyone you like enough to arm."),
            tiers=[
                ("Ember",     "A burn that will not go out.", 0),
                ("Backdraft", "Set the heat now. Let it detonate later.", 30),
                ("Kindling",  "Lend the burn to an ally's weapon.", 60),
                ("Hearth That Will Not Go Out", "Domain Expansion.", 90),
            ],
        ),
        "timestop": dict(
            name="Stillness",
            jp="Teishi — the Held Second",
            tag="Control",
            scales="control",
            blurb=("You take a second out of the world and stand in it alone. It is not "
                   "speed and it is not foresight — the second simply does not happen "
                   "until you let it."),
            verb="Hold",
            verb_desc=("Take a period back. Spend most of your reserve and the hour does "
                       "not pass — you get to do something else with it."),
            tiers=[
                ("Stutter",   "A held half-second. Enough to be somewhere else.", 0),
                ("Held Second", "A full second, and you can move inside it.", 30),
                ("Arrest",    "Long enough to walk across a room nobody is crossing.", 60),
                ("The Second That Did Not Happen", "Domain Expansion.", 90),
            ],
        ),
    }

    def tech():
        return TECHNIQUES[store.technique]

    def tech_stat():
        """The stat this technique scales off."""
        return getattr(store, tech()["scales"])

    def tech_tier():
        """(index, name, description) of the highest unlocked tier."""
        t = tech()
        stat = tech_stat()
        idx = 0
        for i, (nm, desc, req) in enumerate(t["tiers"]):
            if stat >= req:
                idx = i
        nm, desc, req = t["tiers"][idx]
        return idx, nm, desc

    def next_tier():
        """(name, requirement) of the next locked tier, or None."""
        t = tech()
        stat = tech_stat()
        for nm, desc, req in t["tiers"]:
            if stat < req:
                return nm, req
        return None

    ## Energy -------------------------------------------------------------------

    def ce_pct():
        return int(100.0 * store.ce / max(1, store.ce_max))

    def spend_ce(amount):
        """Spend reserve. Returns False (and spends nothing) if you can't afford it."""
        if store.ce < amount:
            return False
        store.ce -= amount
        renpy.restart_interaction()
        return True

    def restore_ce(amount):
        store.ce = min(store.ce_max, store.ce + amount)

    def spend_stamina(amount):
        store.stamina = max(0, store.stamina - amount)

    def gain(stat, amount, quiet=False):
        """Raise control / output / insight, with diminishing returns near the cap."""
        cur = getattr(store, stat)
        if cur >= 60:
            amount = max(1, int(amount * 0.6))
        if cur >= 85:
            amount = max(1, int(amount * 0.5))
        before_tier = tech_tier()[0]
        setattr(store, stat, min(100, cur + amount))
        after = getattr(store, stat)
        if not quiet and after != cur:
            renpy.notify("%s +%d" % (stat.capitalize(), after - cur))
        if tech_tier()[0] > before_tier:
            renpy.notify("Technique advanced — %s" % tech_tier()[1])
            flag("tier_" + str(tech_tier()[0]))

    def tech_name():
        return tech()["name"]

    def add_ce(amount):
        """Prologue-era shim: raise whichever stat this technique scales off."""
        gain(tech()["scales"], amount, quiet=(amount < 0))

    def grade_name():
        return {4: "Grade 4", 3: "Grade 3", 2: "Semi-Grade 2",
                1: "Grade 2", 0: "Grade 1"}.get(store.grade, "Grade 4")


## Stats ########################################################################

default technique = "filament"

default ce      = 60      # spendable reserve
default ce_max  = 60
default control = 12      # precision, technique shaping
default output  = 10      # raw destructive force
default insight = 10      # reading cursed energy, people, rooms
default grade   = 4
