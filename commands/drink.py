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
        obj = caller.search(self.target, location=caller.location)
        if not obj:
            return
        if not obj.attributes.get("is_water_source", default=False):
            caller.msg("You can't drink from that.")
            return
        caller.decrease_thirst(20)
        caller.msg(f"You drink from {obj.get_display_name(caller)}.")
        if caller.location:
            caller.location.msg_contents(
                f"$You() $conj(drink) from {obj.get_display_name(caller.location)}.",
                exclude=caller,
                from_obj=caller,
            )
