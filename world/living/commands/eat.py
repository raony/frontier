"""Eat command for consuming Food objects."""

from commands.command import Command


class CmdEat(Command):
    """Eat an edible item to reduce hunger."""

    key = "eat"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target = self.args.strip()

        if not target:
            caller.msg("What do you want to eat?")
            return

        obj = caller.search_item(target)
        if not obj:
            caller.msg(f"You don't have {target}.")
            return
        if not hasattr(obj, "food"):
            caller.msg("You can't eat that.")
            return
        if not obj.food.can_eat(caller):
            caller.msg("It doesn't look edible.")
            return
        if obj.food.eaten_percentage == 1:
            caller.msg(f"There's nothing left of {obj.get_display_name(caller)} to eat.")
            return

        obj.food.eat(caller)
        caller.location.msg_contents(
            f"$You() $conj(eat) a portion of $obj(obj).",
            mapping={"obj": obj},
            from_obj=caller
        )
