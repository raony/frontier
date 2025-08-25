from commands.command import Command
from world.living.perception import MsgObj


class CmdStand(Command):
    """Stand up from resting.

    Usage:
      stand
    """

    key = "stand"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not getattr(caller, "is_resting", False):
            caller.msg("You are already standing.")
            return
        caller.stop_resting()
        msg_content = "$You() $conj(stand) up."
        caller.location.msg_contents(
            msg_content,
            from_obj=caller,
            msg_obj=MsgObj(visual=msg_content, sound="You hear something move.").to_dict()
        )
