"""Eat command for consuming Food objects."""

from commands.command import Command
from world.utils import DisplayNameWrapper


class CmdEat(Command):
    """Eat an edible item to reduce hunger.

    Usage:
      eat <item>

    Examples:
      eat apple
      eat bread
      eat roasted chicken

    Consumes a portion of food from your inventory to reduce hunger.
    Most foods can be eaten in multiple portions.
    """

    key = "eat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target = self.args.strip()

        if not target:
            return caller.msg("What do you want to eat?")

        obj = caller.search_item(target)
        if not obj:
            return caller.msg(f"You don't have {target}.")
        if not hasattr(obj, "food"):
            return caller.msg("You can't eat that.")
        if not obj.food.can_eat(caller):
            return caller.msg("It doesn't look edible.")
        if obj.food.eaten_percentage == 1:
            return caller.msg(f"There's nothing left of {self.get_display_name(obj)} to eat.")

        obj.food.eat(caller)
        caller.location.msg_contents(
            "$You() $conj(eat) a portion of $obj(food).",
            from_obj=caller,
            mapping={"food": DisplayNameWrapper(obj, command_narration=True)},
        )
