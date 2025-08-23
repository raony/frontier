from commands.command import Command


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
        caller.location.msg_contents(
            f"$You() $conj(lie) down to rest.",
            from_obj=caller
        )
