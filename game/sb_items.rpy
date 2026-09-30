################################################################################
## Cursed Bonds — items, equipment and the armory.
##
## WP6 owns this file (PHASE1_DESIGN.md 3.8, 4.9). WP0 wrote the frozen
## signatures below as stubs, so other packages can code against them. The
## inventory counters and yen already work.
################################################################################

init -1 python:

    ## id -> dict(name, kind, grade, special, sealed, stack, desc, effect, fx,
    ## source, from_flag, hidden). (WP0 stub: empty.)
    ITEMS = {}

    ## Inventory ------------------------------------------------------------------

    def give_item(id, n=1, quiet=False):
        """WP6. Add n of an item, with a toast (kind item). (WP0 stub: counts only.)"""
        if n > 0:
            store.inventory[id] = store.inventory.get(id, 0) + n

    def take_item(id, n=1):
        """WP6. Remove n of an item. False (and nothing removed) if there aren't enough."""
        have = store.inventory.get(id, 0)
        if have < n:
            return False
        if have == n:
            del store.inventory[id]
        else:
            store.inventory[id] = have - n
        return True

    def has_item(id):
        """WP6. True if at least one is in the inventory."""
        return store.inventory.get(id, 0) > 0

    def item_count(id):
        """WP6. How many are in the inventory."""
        return store.inventory.get(id, 0)

    def items_in(kind):
        """WP6. The ids of owned items of a kind."""
        return [i for i in store.inventory if store.inventory[i] > 0
                and ITEMS.get(i, {}).get("kind") == kind]

    def add_yen(n):
        """WP6. Add yen."""
        store.yen += n

    def sync_keepsakes():
        """WP6. Grants keepsakes and mission items from flags, idempotently. (WP0 stub: no-op.)"""
        return

    ## Equipment ------------------------------------------------------------------

    def can_wear(id):
        """WP6. (ok, reason) for wearing a talisman. (WP0 stub: (False, "Later").)"""
        return (False, "Later")

    def equip_talisman(id):
        """WP6. Wear a talisman in a free slot. (WP0 stub: no-op.)"""
        return

    def unequip_talisman(id):
        """WP6. Take a talisman off. (WP0 stub: no-op.)"""
        return

    def equip_tool(id):
        """WP6. Hold a cursed tool, or None for bare hands. (WP0 stub: no-op.)"""
        return

    ## The armory -----------------------------------------------------------------

    def armory_open_now():
        """WP6. The armory action is offered: in the storehouse, with armory_open. (WP0 stub: False.)"""
        return False

    def armory_tools():
        """WP6. [(id, state, reason)] for every tool on the racks. (WP0 stub: [].)"""
        return []


## WP6. The armory action. (WP0 stub: returns.)
label sb_do_armory:
    return

## WP6. The racks. (WP0 stub: empty.)
screen armory():
    tag sandbox
    pass


default inventory = {}
default yen = 0
