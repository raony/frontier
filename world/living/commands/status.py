"""Status command to display survival need levels in text form."""

from commands.command import Command


class CmdStatus(Command):
    """Show your current condition without revealing exact numbers.

    Displays text labels for hunger, thirst, and tiredness.
    """

    key = "status"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller

        # Check if caller has metabolism system
        if not hasattr(caller, "hunger"):
            caller.msg("You don't have needs to report.")
            return

        # Get status labels from metabolism handlers
        hunger_label = caller.hunger.status() or "sated"
        thirst_label = caller.thirst.status() or "quenched"
        tired_label = caller.tiredness.status() or "rested"

        lines = [
            "You check your condition:",
            f"  Hunger: {hunger_label}",
            f"  Thirst: {thirst_label}",
            f"  Tiredness: {tired_label}",
        ]
        caller.msg("\n".join(lines))
