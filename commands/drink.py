from evennia.commands.command import Command

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
        objs = caller.search(
            self.target,
            location=caller.location,
            quiet=True,
            typeclass="typeclasses.liquid.LiquidContainerMixin",
        )
        if not objs:
            caller.msg("You can't drink from that.")
            return
        obj = objs[0]
        obj.drink_liquid(caller)
