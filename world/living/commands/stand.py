from commands.command import Command


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
        caller.location.msg_contents(
            f"$You() $conj(stand) up.",
            from_obj=caller
        )
