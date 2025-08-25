from commands.command import Command
from world.physical.liquid import LiquidContainer, Water
from world.utils import DisplayNameWrapper
from world.living.perception import MsgObj


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
            return caller.msg("Usage: fill <dest>=<source>")

        dest = caller.search_item(dest_name)
        if not dest:
            return caller.msg(f"You don't see {dest_name}.")

        source = caller.search_item(source_name)
        if not source:
            return caller.msg(f"You don't see {source_name}.")

        if not dest.is_typeclass(LiquidContainer, exact=False):
            return caller.msg(f"You can't fill {self.get_display_name(dest)}.")

        if dest.is_full:
            return caller.msg(f"{self.get_display_name(dest)} is full.")

        if not source.is_typeclass(Water, exact=False) and not source.is_typeclass(LiquidContainer, exact=False):
            return caller.msg(f"You can't fill {self.get_display_name(dest)} with {self.get_display_name(source)}.")

        if source.is_typeclass(LiquidContainer, exact=False):
            source = source.liquid

        dest.fill(source)
        msg_content = "$You() fill the $obj(dest) from $obj(source)."
        caller.location.msg_contents(
            msg_content,
            from_obj=caller,
            mapping={
                "dest": DisplayNameWrapper(dest, command_narration=True),
                "source": DisplayNameWrapper(source, command_narration=True),
            },
            msg_obj=MsgObj(visual=msg_content, sound="You hear liquid pouring.").to_dict()
        )
