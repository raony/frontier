from commands.command import Command
from world.physical.liquid import LiquidContainer
from typeclasses.rooms import Room

class CmdEmpty(Command):
    """Empty a liquid container.

    Usage:
      empty <source>=<destination>
      empty <source>
    """

    key = "empty"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        source_name = self.lhs
        dest_name = self.rhs

        if not source_name:
            caller.msg("Usage: empty <source>=<destination> or empty <source>")
            return

        source = caller.search_item(source_name)
        if not source:
            caller.msg(f"You don't see {source_name}.")
            return

        if dest_name:
            dest = caller.search_item(dest_name)
            if not dest:
                caller.msg(f"You don't see {dest_name}.")
                return
        else:
            dest = caller.location

        if not source.is_typeclass(LiquidContainer, exact=False):
            caller.msg(f"You can't empty {source.get_display_name(caller)}.")
            return

        if not dest.is_typeclass(LiquidContainer, exact=False) and not dest.is_typeclass(Room, exact=False):
            caller.msg(f"You can't empty {source.get_display_name(caller)} into {dest.get_display_name(caller)}.")
            return

        if dest.is_typeclass(LiquidContainer, exact=False):
            if dest.is_full:
                caller.msg(f"{dest.get_display_name(caller)} is full.")
            dest.fill(source.liquid)
        elif dest.is_typeclass(Room, exact=False):
            source.liquid.move_to(dest, quiet=True)
            caller.location.msg_contents(
                "$You() empty the $obj{source} into the floor.",
                from_obj=source,
                mapping={
                    "source": source,
                }
            )
        else:
            caller.msg(f"{dest.get_display_name(caller)} can't hold the liquid.")
