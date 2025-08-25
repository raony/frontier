from evennia import AttributeProperty, create_object
from typeclasses.objects import Object

class Water(Object):
    type = AttributeProperty(default="water", category="physical")
    potable = AttributeProperty(default=True, category="physical")

    def get_display_name(self, looker):
        if self.location.is_typeclass("typeclasses.rooms.Room", exact=False):
            if self.weight.value < 1000:
                return f"a drop of {self.type}"
            if self.weight.value < 10000:
                return f"a puddle of {self.type}"
            return f"there is {self.type} everywhere"
        return super().get_display_name(looker)

    def get_numbered_name(self, count, looker, **kwargs):
        kwargs["no_article"] = True
        return super().get_numbered_name(count, looker, **kwargs)

    def drain(self, amount):
        if amount >= self.weight.value:
            return self
        else:
            drained = self.copy(new_key=self.key, new_location=self.location)
            drained.weight.value = amount
            return drained

    def mix(self, liquid):
        self.weight.value += liquid.weight.value
        liquid.delete()


class LiquidContainer(Object):
    liquid_capacity = AttributeProperty(default=1000, category="physical")

    @property
    def amount(self):
        return self.liquid.weight.value if self.liquid else 0

    def fill(self, source):
        if not source.is_typeclass(Water, exact=False):
            return False

        amount = min(source.weight.value, self.liquid_capacity - self.amount)

        transferred = source.drain(amount)

        if self.liquid:
            self.liquid.mix(transferred)
        else:
            transferred.move_to(self)

        return True

    @property
    def liquid(self):
        for content in self.contents:
            if content.is_typeclass(Water, exact=False):
                return content
        return None

    def get_display_name(self, looker):
        name = super().get_display_name(looker)
        if self.location == looker:
            return f"{self.fill_state} {name}"
        return name

    @property
    def fill_state(self):
        if self.amount == 0:
            return "empty"
        if self.amount < self.liquid_capacity * 0.15:
            return "almost empty"
        if self.amount < self.liquid_capacity * 0.375:
            return "1/4 full"
        if self.amount < self.liquid_capacity * 0.625:
            return "1/2 full"
        if self.amount < self.liquid_capacity * 0.875:
            return "3/4 full"
        if self.amount < self.liquid_capacity:
            return "almost full"
        return "full"