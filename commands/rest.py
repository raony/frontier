from evennia.utils import utils
from .command import Command


class CmdRest(Command):
    """Toggle resting to recover tiredness."""

    key = "rest"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not utils.inherits_from(caller, "typeclasses.characters.LivingMixin"):
            caller.msg("You can't rest.")
            return
        if caller.db.is_resting:
            caller.db.is_resting = False
            caller.msg("You stop resting.")
            location = caller.location
            if location:
                location.msg_contents(
                    f"{caller.get_display_name(location)} gets back up.",
                    exclude=caller,
                )
        else:
            caller.db.is_resting = True
            caller.msg("You settle down to rest.")
            location = caller.location
            if location:
                location.msg_contents(
                    f"{caller.get_display_name(location)} lies down to rest.",
                    exclude=caller,
                )
