"""Eat command for consuming Food objects."""

from .command import Command
from evennia.utils.utils import inherits_from


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

        objs = caller.search(
            self.args,
            location=caller,
            candidates=caller.contents + (caller.location.contents if caller.location else []),
            quiet=True,
        )
        if not objs:
            return
        obj = objs[0]
        if not inherits_from(obj, "typeclasses.food.FoodMixin"):
            caller.msg("You can't eat that.")
            return
        obj.eat(caller)
