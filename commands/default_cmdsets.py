"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from .skills import CmdSkills, CmdCreateSkill, CmdSetSkill
from .resources import CmdCreateResource
from .time import CmdSetDateTime, CmdSetTime
from .external import CmdMakeExternal
from .hex import CmdSetHex, CmdWeather
from .weight import CmdSetWeight
from world.physical.commands import CmdFill, CmdEmpty, CmdStore


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """Restore default Evennia character command set as baseline."""

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        # Admin maintenance command - available even when dead (locks restrict use)
        self.add(CmdCreateSkill())
        self.add(CmdSetSkill())
        self.add(CmdCreateResource())
        self.add(CmdSetDateTime())
        self.add(CmdSetTime())
        self.add(CmdMakeExternal())
        # Builder utilities
        self.add(CmdSetHex())
        self.add(CmdWeather())
        self.add(CmdSetWeight())
        self.add(CmdSkills())
        self.add(CmdFill())
        self.add(CmdEmpty())
        self.add(CmdStore())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        # Intentionally minimal. Gameplay commands live in AliveCmdSet.
