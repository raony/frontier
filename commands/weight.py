"""Weight command to display weight information for items."""

from .command import Command


class CmdWeight(Command):
    """Check the weight of items or your inventory.

    Usage:
      weight                    - Show total weight of your inventory
      weight <item>            - Show weight of a specific item
    """

    key = "weight"
    aliases = ["wt"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target = self.lhs

        if not target:
            lines = ["Your inventory weight:"]
            if caller.contents:
                total_weight = 0
                for obj in caller.contents:
                    if not hasattr(obj, 'total_weight'):
                        continue
                    lines.append(f"  {obj.get_display_name(caller)}: {obj.total_weight}g")
                    total_weight += obj.total_weight
                lines.append(f"Total: {total_weight}g")
            else:
                lines.append("Your inventory is empty.")

            caller.msg("\n".join(lines))
            return

        obj = caller.quiet_search(target)
        if not obj:
            caller.msg(f"You can't find {target}.")
            return

        if not hasattr(obj, 'total_weight'):
            caller.msg(f"What do you mean?")
            return

        caller.msg(f"{obj.get_display_name(caller)} weighs {obj.total_weight}g.")


class CmdSetWeight(Command):
    """Set the weight of an item (Builder only).

    Usage:
      setweight <item> = <weight>
    """

    key = "setweight"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        item_key = self.lhs
        weight = self.rhs

        if not item_key or not weight:
            caller.msg("Usage: setweight <item> = <weight>")
            return

        obj = caller.quiet_search(item_key)
        if not obj:
            caller.msg(f"You can't find {item_key}.")
            return

        if not hasattr(obj, 'set_weight'):
            caller.msg(f"{obj.get_display_name(caller)} doesn't support weight setting.")
            return

        try:
            obj.set_weight(weight)
            caller.msg(f"Set {obj.get_display_name(caller)}'s weight to {weight}g.")
        except ValueError as e:
            caller.msg(e)
