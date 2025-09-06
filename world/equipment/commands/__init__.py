from .hold import CmdHold
from .equip import CmdEquip
from evennia import default_cmds

class HoldCmdSet(default_cmds.CharacterCmdSet):
    key = "Hold"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdHold())
        self.add(CmdEquip())

__all__ = [
    'HoldCmdSet',
    'CmdHold',
    'CmdEquip',
]