"""Eat command for consuming Food objects."""
from evennia.utils.utils import inherits_from

from .command import Command


class CmdEat(Command):
    """Eat an edible item to reduce hunger."""

    key = "eat"
    locks = "cmd:all()"
    arg_regex = r"\s|$"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to eat?")
            return

        obj = caller.search(
            self.args,
            location=caller,
            candidates=caller.contents + caller.location.contents,
        )
        if not obj:
            return

        if not inherits_from(obj, "typeclasses.food.FoodMixin"):
            caller.msg("You can't eat that.")
            return

        obj.eat(caller)

