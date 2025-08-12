from .command import Command


class CmdStand(Command):
    """Stand up from resting.

    Usage:
      stand
    """

    key = "stand"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not caller:
            return
        if not getattr(caller, "is_resting", False):
            caller.msg("You are already standing.")
            return
        caller.is_resting = False
        caller.msg("You stand up.")
        location = caller.location
        if location:
            location.msg_contents(
                f"{caller.get_display_name(location)} gets back up.",
                exclude=caller,
            )
