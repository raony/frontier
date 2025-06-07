"""Eat command for consuming Food objects."""

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

        objs = caller.search(
            self.args,
            location=caller,
            candidates=caller.contents + caller.location.contents,
            quiet=True,
            typeclass="typeclasses.food.FoodMixin",
        )
        if not objs:
            return
        obj = objs[0]

        obj.eat(caller)

