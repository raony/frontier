from evennia.utils.utils import lazy_property

class FoodHandler:
    """Handler for food objects."""

    def __init__(self, obj):
        self.obj = obj
        obj.tags.add("food", category="food")
        self._load()

    def _load(self):
        self._calories = self.obj.attributes.get("db_calories", default=10, category="food")
        self._total_calories = self.obj.attributes.get("db_total_calories", default=10, category="food")
        self._waste_proportion = self.obj.attributes.get("db_waste_proportion", default=0.1, category="food")

    @property
    def calories(self):
        return self._calories

    @calories.setter
    def calories(self, value):
        self._calories = value
        self.obj.attributes.add("db_calories", self.calories, category="food")

    @property
    def total_calories(self):
        return self._total_calories

    @total_calories.setter
    def total_calories(self, value):
        self._total_calories = value
        self.obj.attributes.add("db_total_calories", self.total_calories, category="food")

    @property
    def waste_proportion(self):
        return self._waste_proportion

    @waste_proportion.setter
    def waste_proportion(self, value):
        self._waste_proportion = value
        self.obj.attributes.add("db_waste_proportion", self.waste_proportion, category="food")

    @property
    def eaten_percentage(self):
        return 1 - (self.calories / self.total_calories)

    def can_eat(self, eater):
        return True

    def eat(self, eater):
        if hasattr(eater, "eat"):
            calories = min(self.calories, 7)
            bite_size = calories / self.calories
            weight_eaten = (1 - self.waste_proportion) * bite_size
            eater.eat(self, calories=calories)
            self.calories -= calories
            self.obj.weight.decrease(weight_eaten)
            self.waste_proportion = self.waste_proportion/(1 - weight_eaten)
            return calories
        return 0


class FoodMixin:
    @lazy_property
    def food(self) -> FoodHandler:
        return FoodHandler(self)

    def reset_food(self):
        self.food.calories = self.food.total_calories
        self.weight.value = self.default_weight

    def get_display_name(self, looker):
        name = super().get_display_name(looker)
        if self.food.eaten_percentage == 0:
            return name

        if self.food.eaten_percentage == 1:
            return f"rest of {name}"
        if self.food.eaten_percentage > 0.5:
            return f"partially eaten {name}"
        if self.food.eaten_percentage > 0:
            return f"bitten {name}"