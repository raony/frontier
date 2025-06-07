"""Food mixin and object type for edible items."""

from evennia.utils.utils import inherits_from
from .objects import Object


class FoodMixin:
    """Mixin that marks an object as edible."""

    calories = 1

    def at_object_creation(self):
        super().at_object_creation()
        if self.db.calories is None:
            self.db.calories = self.calories

    def eat(self, eater):
        """Consume this item, reducing eater hunger."""
        calories = max(1, min(int(self.db.calories or self.calories), 7))
        if inherits_from(eater, "typeclasses.characters.LivingMixin"):
            eater.decrease_hunger(calories)
        eater.msg(f"You eat {self.key}.")
        if self.location:
            self.location.msg_contents(
                f"$You() eats {self.get_display_name(self.location, looker=eater)}.",
                from_obj=eater,
                exclude=eater,
            )
        self.delete()


class Food(FoodMixin, Object):
    """Simple edible object."""
    pass

