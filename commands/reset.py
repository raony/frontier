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

        caller.msg(caller.reset_and_revive())
