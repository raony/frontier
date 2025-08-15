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

        # Use the new living module functionality
        if hasattr(caller, 'reset_and_revive'):
            message = caller.reset_and_revive()
            caller.msg(message)
        else:
            # Fallback for non-living beings or old system
            caller.is_dead = False
            caller.is_living = True
            caller.is_resting = False
            if hasattr(caller, "start_metabolism_script"):
                caller.start_metabolism_script()
            if hasattr(caller, "update_living_status"):
                caller.update_living_status()
            caller.msg("You feel refreshed and alive. Your needs are reset.")
