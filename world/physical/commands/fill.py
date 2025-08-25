from commands.command import Command
from world.physical.liquid import LiquidContainer, Water


class CmdFill(Command):
    """Fill one liquid container from another.

    Usage:
      fill <dest>=<source>
    """

    key = "fill"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        dest_name = self.lhs
        source_name = self.rhs

        if not dest_name or not source_name:
            self.caller.msg("Usage: fill <dest> <source>")
            return

        dest = caller.search_item(dest_name)
        if not dest:
            caller.msg(f"You don't see {dest_name}.")
            return

        source = caller.search_item(source_name)
        if not source:
            caller.msg(f"You don't see {source_name}.")
            return

        if not dest.is_typeclass(LiquidContainer, exact=False):
            caller.msg(f"You can't fill {dest_name}.")
            return

        if not source.is_typeclass(Water, exact=False) and not source.is_typeclass(LiquidContainer, exact=False):
            caller.msg(f"You can't fill {dest_name} with {source_name}.")
            return

        if source.is_typeclass(LiquidContainer, exact=False):
            source = source.liquid

        dest.fill(source)
        caller.location.msg_contents(
            "$You() fill the $obj{dest} from $obj{source}.",
            from_obj=caller,
            mapping={
                "dest": dest,
                "source": source,
            }
        )
