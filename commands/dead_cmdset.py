from evennia import CmdSet
from evennia.commands.command import Command


class CmdDeadLook(Command):
    """Simple look replacement for dead characters."""

    key = "look"
    aliases = ["l", "examine", "exa", "search"]
    locks = "cmd:all()"

    def func(self):
        self.caller.msg("Everything is dark. You are dead.")


class CmdDeadNoCommand(Command):
    """Catch-all command blocking actions when dead."""

    key = "dead_noop"
    aliases = ["*"]
    locks = "cmd:all()"
    arg_regex = r".*"

    def func(self):
        self.caller.msg("You are dead and cannot do that.")


class DeadCmdSet(CmdSet):
    """Command set for dead characters."""

    key = "DeadCmdSet"
    priority = 110
    mergetype = "Replace"

    def at_cmdset_creation(self):
        self.add(CmdDeadLook())
        self.add(CmdDeadNoCommand())
