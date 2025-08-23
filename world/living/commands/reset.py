"""Reset character survival stats and revive command."""

from commands.command import Command


class CmdResetChar(Command):
    """Reset your character's survival needs and revive.

    Usage:
      resetchar <target>

    Sets hunger, thirst, tiredness to 0 and ensures you are alive.
    """

    key = "resetchar"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        target = self.lhs
        if not target:
            target = caller
        else:
            target = caller.search(target)

        if hasattr(target, "reset_and_revive"):
            target.reset_and_revive()
            if target != caller:
                caller.msg(f"{target.get_display_name(caller)} has been revived and their needs have been reset.")
            target.msg(f"You have been revived and your needs have been reset.")
        else:
            caller.msg(f"{target.get_display_name(caller)} is not a living being.")
