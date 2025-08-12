from evennia import CmdSet
from evennia.commands.command import Command


class _DeadBlock(Command):
    """Base blocker for commands not allowed while dead."""

    locks = "cmd:all()"
    dead_message = "You are dead and cannot do that."

    def func(self):
        self.caller.msg(self.dead_message)


class CmdDeadLook(_DeadBlock):
    """Block look with a dead-specific message."""

    key = "look"
    aliases = ["l", "ls"]
    dead_message = "Everything is dark. You are dead."


class CmdDeadSay(_DeadBlock):
    key = "say"


class CmdDeadPose(_DeadBlock):
    key = "pose"
    aliases = [":"]


class CmdDeadWhisper(_DeadBlock):
    key = "whisper"


class CmdDeadGet(_DeadBlock):
    key = "get"


class CmdDeadGive(_DeadBlock):
    key = "give"


class CmdDeadDrop(_DeadBlock):
    key = "drop"


class CmdDeadInventory(_DeadBlock):
    key = "inventory"
    aliases = ["inv", "i"]


class CmdDeadOOC(_DeadBlock):
    key = "ooc"


class DeadCmdSet(CmdSet):
    """Command set for dead characters."""

    key = "DeadCmdSet"
    priority = 110

    def at_cmdset_creation(self):
        self.add(CmdDeadLook())
        # Block common living-only commands while dead
        self.add(CmdDeadSay())
        self.add(CmdDeadPose())
        self.add(CmdDeadWhisper())
        self.add(CmdDeadGet())
        self.add(CmdDeadGive())
        self.add(CmdDeadDrop())
        self.add(CmdDeadInventory())
        self.add(CmdDeadOOC())
