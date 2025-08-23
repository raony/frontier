from commands.command import Command


class CmdDarkvision(Command):
    """Toggle darkvision for builders to see in dark areas.

    Usage:
      darkvision
    """

    key = "darkvision"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        if not hasattr(caller, "vision"):
            caller.msg("You don't have light perception.")
            return

        caller.vision.enable()
        caller.vision.light_threshold = 0

        caller.msg("Darkvision enabled. You can now see in complete darkness.")