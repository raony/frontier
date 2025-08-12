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
                f"$You() eats {self.get_display_name(eater)}.",
                from_obj=eater,
                exclude=eater,
            )
        self.delete()


class Food(FoodMixin, Object):
    """Simple edible object."""
    pass


class PortionedFoodMixin(FoodMixin):
    """Edible object that contains multiple portions.

    Each time it's eaten, one portion is consumed and hunger is reduced
    by `calories_per_part`. The object is deleted when no portions remain.
    The description reflects remaining portions.
    """

    parts_total = 4
    calories_per_part = 2

    def at_object_creation(self):
        super().at_object_creation()
        if self.db.parts_total is None:
            self.db.parts_total = int(self.parts_total)
        if self.db.parts_left is None:
            self.db.parts_left = int(self.db.parts_total)
        if self.db.calories_per_part is None:
            self.db.calories_per_part = int(self.calories_per_part)

    def get_display_desc(self, looker, **kwargs):
        """Return description including portions remaining."""
        desc = super().get_display_desc(looker, **kwargs)
        total = max(1, int(self.db.parts_total or self.parts_total))
        left = max(0, min(int(self.db.parts_left or total), total))
        portion_text = f" It has {left} of {total} portions left."
        if desc:
            return f"{desc}{portion_text}"
        return portion_text.strip()

    def eat(self, eater):
        """Consume one portion, reducing hunger and decrementing parts."""
        if not self.db.parts_left:
            eater.msg(f"There is nothing left of {self.get_display_name(eater)} to eat.")
            return
        calories = max(1, min(int(self.db.calories_per_part or self.calories_per_part), 7))
        from evennia.utils.utils import inherits_from
        if inherits_from(eater, "typeclasses.characters.LivingMixin"):
            eater.decrease_hunger(calories)
        eater.msg(f"You eat a portion of {self.get_display_name(eater)}.")
        if self.location:
            self.location.msg_contents(
                f"$You() eats a portion of {self.get_display_name(eater)}.",
                from_obj=eater,
                exclude=eater,
            )
        self.db.parts_left = max((self.db.parts_left or 0) - 1, 0)
        if self.db.parts_left <= 0:
            eater.msg(f"You finish the last of {self.get_display_name(eater)}.")
            self.delete()


class PortionedFood(PortionedFoodMixin, Object):
    """Generic portioned food typeclass."""
    pass


class RoastedChicken(PortionedFood):
    """Roasted chicken with multiple edible portions."""

    parts_total = 6
    calories_per_part = 3
