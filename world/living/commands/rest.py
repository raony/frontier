from commands.command import Command
from world.living.perception import MsgObj


class CmdRest(Command):
    """Toggle resting to recover tiredness."""

    key = "rest"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not hasattr(caller, "is_resting"):
            caller.msg("You can't rest.")
            return
        if caller.is_resting:
            caller.msg("You are already resting. Use 'stand' to get up.")
            return
        caller.start_resting()
        msg_content = "$You() $conj(lie) down to rest."
        caller.location.msg_contents(
            msg_content,
            from_obj=caller,
            msg_obj=MsgObj(visual=msg_content, sound="You hear something move.").to_dict()
        )
