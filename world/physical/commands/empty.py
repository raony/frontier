from commands.command import Command
from world.physical.liquid import LiquidContainer, LiquidContainerMixin
from typeclasses.rooms import Room
from world.utils import DisplayNameWrapper
from world.living.perception import MsgObj

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
            return caller.msg("Usage: empty <source>=<destination> or empty <source>")

        source = caller.search_item(source_name)
        if not source:
            return caller.msg(f"You don't see {source_name}.")

        if dest_name:
            dest = caller.search_item(dest_name)
            if not dest:
                return caller.msg(f"You don't see {dest_name}.")
        else:
            dest = caller.location

        if not source.is_typeclass(LiquidContainer, exact=False):
            return caller.msg(f"You can't empty {self.get_display_name(source)}.")

        if not dest.is_typeclass(LiquidContainer, exact=False) and not dest.is_typeclass(Room, exact=False):
            return caller.msg(f"You can't empty {self.get_display_name(source)} into {self.get_display_name(dest)}.")

        if dest.is_full:
            return caller.msg(f"{self.get_display_name(dest)} is full.")

        msg_content = f"$You() empty the $obj(source) into the {'floor' if dest.is_typeclass(Room, exact=False) else '$obj(dest)'}"
        caller.location.msg_contents(
            msg_content,
            from_obj=caller,
            mapping={
                "source": DisplayNameWrapper(source, command_narration=True),
                "dest": DisplayNameWrapper(dest, command_narration=True),
            },
            msg_obj=MsgObj(visual=msg_content, sound="You hear liquid splashing.").to_dict()
        )

        dest.fill(source.liquid)