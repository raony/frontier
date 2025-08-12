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
            candidates=(caller.location.contents if caller.location else []),
            quiet=True,
        )
        if not objs:
            caller.msg("You can't drink from that.")
            return
        obj = objs[0]
        # Only allow liquids
        from evennia.utils.utils import inherits_from
        if not inherits_from(obj, "typeclasses.liquid.LiquidContainerMixin"):
            caller.msg("You can't drink from that.")
            return
        obj.drink_liquid(caller)
