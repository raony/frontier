"""Reset character survival stats and revive command."""

from .command import Command
from commands.dead_cmdset import DeadCmdSet


class CmdResetChar(Command):
    """Reset your character's survival needs and revive.

    Usage:
      resetchar

    Sets hunger, thirst, tiredness to 0 and ensures you are alive.
    """

    key = "resetchar"
    locks = "cmd:perm(Admin) or perm(Builder) or perm(Developer) or superuser()"
    arg_regex = r"$"

    def func(self):
        caller = self.caller
        if not caller:
            return

        # Reset survival stats to 0
        caller.hunger = 0
        caller.thirst = 0
        caller.tiredness = 0

        # Clear threshold message trackers
        if hasattr(caller, "ndb"):
            caller.ndb.hunger_msg_level = 0
            caller.ndb.thirst_msg_level = 0
            caller.ndb.tiredness_msg_level = 0

        # Use the living module functionality
        message = caller.reset_and_revive()
        caller.msg(message)
