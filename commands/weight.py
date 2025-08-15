"""Weight command to display weight information for items."""

from .command import Command


class CmdWeight(Command):
    """Check the weight of items or your inventory.

    Usage:
      weight                    - Show total weight of your inventory
      weight <item>            - Show weight of a specific item
      weight all               - Show weight of all items in your inventory
    """

    key = "weight"
    aliases = ["wt"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target = self.args.strip()

        if not target:
            # Show total inventory weight
            total_weight = 0
            items = []

            for obj in caller.contents:
                if hasattr(obj, 'get_weight'):
                    weight = obj.get_weight()
                    total_weight += weight
                    items.append((obj, weight))

            if not items:
                caller.msg("Your inventory is empty.")
                return

            lines = ["Your inventory weight:"]
            for obj, weight in sorted(items, key=lambda x: x[1], reverse=True):
                lines.append(f"  {obj.get_display_name(caller)}: {weight}g")
            lines.append(f"Total: {total_weight}g")

            caller.msg("\n".join(lines))
            return

        if target.lower() == "all":
            # Show all items with weights
            items = []
            for obj in caller.contents:
                if hasattr(obj, 'get_weight'):
                    weight = obj.get_weight()
                    items.append((obj, weight))

            if not items:
                caller.msg("Your inventory is empty.")
                return

            lines = ["Items in your inventory:"]
            for obj, weight in sorted(items, key=lambda x: x[1], reverse=True):
                lines.append(f"  {obj.get_display_name(caller)}: {weight}g")

            caller.msg("\n".join(lines))
            return

        # Show weight of specific item
        obj = caller.search(target, quiet=True)
        if not obj:
            caller.msg(f"You don't have {target}.")
            return

        if not hasattr(obj, 'get_weight'):
            caller.msg(f"{obj.get_display_name(caller)} doesn't have a weight.")
            return

        weight = obj.get_weight()
        caller.msg(f"{obj.get_display_name(caller)} weighs {weight}g.")


class CmdSetWeight(Command):
    """Set the weight of an item (Builder only).

    Usage:
      setweight <item> = <weight>
    """

    key = "setweight"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller

        if not self.lhs or not self.rhs:
            caller.msg("Usage: setweight <item> = <weight>")
            return

        obj = caller.search(self.lhs, quiet=True)
        if not obj:
            return

        try:
            weight = int(self.rhs)
            if weight < 0:
                caller.msg("Weight cannot be negative.")
                return
        except ValueError:
            caller.msg("Weight must be a number.")
            return

        if not hasattr(obj, 'set_weight'):
            caller.msg(f"{obj.get_display_name(caller)} doesn't support weight setting.")
            return

        obj.set_weight(weight)
        caller.msg(f"Set {obj.get_display_name(caller)}'s weight to {weight}g.")
