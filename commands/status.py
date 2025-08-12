"""Status command to display survival need levels in text form."""

from .command import Command


class CmdStatus(Command):
    """Show your current condition without revealing exact numbers.

    Displays text labels for hunger, thirst, and tiredness.
    """

    key = "status"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not hasattr(caller, "_hunger_level"):
            caller.msg("You don't have needs to report.")
            return

        # Prefer public helpers if available; fall back to level mapping.
        if hasattr(caller, "get_hunger_label"):
            hunger_label = caller.get_hunger_label()
        else:
            level = caller._hunger_level()
            hunger_label = ["sated", "hungry", "starving", "starving to death"][level]

        if hasattr(caller, "get_thirst_label"):
            thirst_label = caller.get_thirst_label()
        else:
            level = caller._thirst_level()
            thirst_label = ["quenched", "thirsty", "parched", "dying of thirst"][level]

        if hasattr(caller, "get_tiredness_label"):
            tired_label = caller.get_tiredness_label()
        else:
            level = caller._tiredness_level()
            tired_label = ["rested", "tired", "exhausted", "about to collapse"][level]

        lines = [
            "You check your condition:",
            f"  Hunger: {hunger_label}",
            f"  Thirst: {thirst_label}",
            f"  Tiredness: {tired_label}",
        ]
        caller.msg("\n".join(lines))
