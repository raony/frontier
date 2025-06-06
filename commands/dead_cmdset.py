from evennia import CmdSet
from evennia.commands.command import Command


class CmdDeadLook(Command):
    """Simple look replacement for dead characters."""

    key = "look"
    aliases = ["l", "ls"]
    locks = "cmd:all()"

    def func(self):
        self.caller.msg("Everything is dark. You are dead.")


class DeadCmdSet(CmdSet):
    """Command set for dead characters."""

    key = "DeadCmdSet"
    priority = 110

    def at_cmdset_creation(self):
        self.add(CmdDeadLook())
