from .drink import CmdDrink
from .eat import CmdEat
from .rest import CmdRest
from .stand import CmdStand
from .kill import CmdKill
from .reset import CmdResetChar
from .darkvision import CmdDarkvision
from evennia import default_cmds

class AliveCmdSet(default_cmds.CharacterCmdSet):
    """
    Commands available only to living characters.
    """

    key = "AliveCharacter"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdEat())
        self.add(CmdDrink())
        self.add(CmdRest())
        self.add(CmdStand())

class LivingBuilderCmdSet(default_cmds.CharacterCmdSet):

    key = "LivingBuilderCharacter"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(CmdResetChar())
        self.add(CmdKill())
        self.add(CmdDarkvision())

__all__ = ["CmdDrink", "CmdEat", "CmdRest", "CmdStand", "AliveCmdSet", "LivingBuilderCmdSet"]