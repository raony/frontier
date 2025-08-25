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
        self.send_room_message(
            "$You() $conj(stand) up.",
            sound="You hear something move."
        )
