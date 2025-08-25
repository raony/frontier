from evennia.utils.utils import lazy_property

class WeightHandler:
    """Handler for weight objects."""

    def __init__(self, obj):
        self.obj = obj
        self._load()

    @property
    def value(self):
        return self._weight

    @value.setter
    def value(self, value):
        self._weight = value
        self._save()

    @property
    def total(self):
        return self.value + sum(item.weight.total for item in self.obj.contents)

    def _load(self):
        self._weight = self.obj.attributes.get("weight", default=0, category="physical")

    def _save(self):
        self.obj.attributes.add("weight", self._weight, category="physical")
        self._load()

    def decrease(self, proportion):
        self.value -= self.value * proportion

    def increase(self, proportion):
        self.value += self.value * proportion

class WeightMixin:
    @lazy_property
    def weight(self):
        return WeightHandler(self)

    def at_object_creation(self):
        super().at_object_creation()
        self.weight.value = self.default_weight

    def get_display_name(self, looker, **kwargs):
        name = super().get_display_name(looker, **kwargs)

        if kwargs.get("command_narration"):
            return name

        if hasattr(looker, 'holding_strength'):
            if self.weight.total <= looker.holding_strength:
                return f"{name} ░"
            elif self.weight.total <= looker.holding_strength * len(looker.held_items.slots):
                return f"{name} ▒"
            else:
                return f"{name} █"

        return name