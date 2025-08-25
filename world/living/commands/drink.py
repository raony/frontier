from commands.command import Command
from world.physical.liquid import LiquidContainer, Water
from world.utils import DisplayNameWrapper


class CmdDrink(Command):
    """Drink from a nearby water source."""

    key = "drink"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target = self.lhs

        if not target:
            return caller.msg("What do you want to drink from?")

        obj = caller.search_item(target)
        if not obj:
            return caller.msg(f"You don't see {target}.")

        if not obj.is_typeclass(LiquidContainer, exact=False) and not obj.is_typeclass(Water, exact=False):
            return caller.msg(f"You can't drink from {self.get_display_name(obj)}.")

        liquid = None
        if obj.is_typeclass(LiquidContainer, exact=False):
            liquid = obj.liquid
            if not liquid:
                return caller.msg(f"{self.get_display_name(obj)} is empty.")
        else:
            liquid = obj

        if not liquid.is_typeclass(Water, exact=False):
            return caller.msg(f"You can't drink {self.get_display_name(liquid)}.")

        if not getattr(liquid, 'potable', True):
            return caller.msg(f"{self.get_display_name(liquid)} is not safe to drink.")

        hydration_amount = min(liquid.weight.value, 200)
        if hydration_amount <= 0:
            return caller.msg(f"There's no {self.get_display_name(liquid)} left to drink.")

        caller.drink(liquid.drain(hydration_amount))

        caller.location.msg_contents(
            "$You() $conj(drink) from $obj(container).",
            from_obj=caller,
            mapping={"container": DisplayNameWrapper(obj, command_narration=True)},
        )
