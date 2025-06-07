from evennia.commands.command import Command
from evennia.utils.utils import inherits_from

class CmdDrink(Command):
    """Drink from a nearby water source."""

    key = "drink"
    locks = "cmd:all()"

    def parse(self):
        """Simple parser to get the target."""
        self.target = self.args.strip()

    def func(self):
        caller = self.caller
        if not self.target:
            caller.msg("Drink from what?")
            return
        obj = caller.search(self.target, location=caller.location)
        if not obj:
            return
        if not inherits_from(obj, "typeclasses.liquid.LiquidContainerMixin") or not obj.has_liquid():
            caller.msg("You can't drink from that.")
            return
        obj.drink_liquid(caller)
