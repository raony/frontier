"""Kill command for testing living/dead state transitions."""

from commands.command import Command


class CmdKill(Command):
    """Kill a living being for testing purposes.

    Usage:
      @kill <target>

    This command kills a living being, setting their state to dead.
    Only available to builders for testing purposes.
    """

    key = "@kill"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        target = self.lhs

        target = caller.search(target)

        if not hasattr(target, 'die'):
            caller.msg(f"{target.get_display_name(caller)} is not a living being.")
            return

        if target.is_dead:
            caller.msg(f"{target.get_display_name(caller)} is already dead.")
            return

        target.die()

        caller.msg(f"You kill {target.get_display_name(caller)}.")