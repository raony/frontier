from evennia import AttributeProperty
from evennia.utils.utils import lazy_property
from evennia.scripts.scripts import DefaultScript
from world.utils import null_func

class MetabolismHandler:
    messages = []
    labels = []

    def __init__(self, obj, attribute=None, thresholds=[7, 30, 60], increase_modifier=1.0):
        self.obj = obj
        self.attribute = attribute
        self.db_attribute = f"db_{attribute}"
        self.thresholds = thresholds
        self.increase_modifier = increase_modifier
        self._load()

    def _load(self):
        self._value = self.obj.attributes.get(self.db_attribute, default=0.0, category="metabolism")

    def _save(self):
        self.obj.attributes.add(self.db_attribute, self._value, category="metabolism")
        self._load()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        before_level = self.level
        before_value = self.value
        self._value = max(0, min(100, value))
        self._save() if before_value != self._value else None
        self.notify() if self.level > before_level else None
        if self._value >= 100:
            self.obj.die()

    @property
    def level(self):
        value = self.value or 0
        for i, threshold in enumerate(reversed(self.thresholds)):
            if value >= threshold:
                return len(self.thresholds) - i
        return 0

    def increase(self, amount=None):
        if not amount:
            amount = 1.0 * self.increase_modifier
        self.value += amount

    def decrease(self, amount):
        self.value -= amount

    def tick(self):
        self.increase()

    def reset(self):
        if self._value > 0:
            self._value = 0
            self._save()

    def notify(self):
        if self.level > 0 and len(self.messages) > self.level:
            self.obj.msg(self.messages[self.level])

    def status(self):
        if self.level > 0 and len(self.labels) > self.level:
            return self.labels[self.level]
        return None

class HungerManager(MetabolismHandler):
    def __init__(self, obj):
        super().__init__(obj, 'hunger', increase_modifier=0.3)

    messages = ["", "You feel hungry.", "You're starving.", "You're gonna die."]
    labels = ["sated", "hungry", "starving", "starving to death"]


class ThirstManager(MetabolismHandler):
    def __init__(self, obj):
        super().__init__(obj, 'thirst', increase_modifier=1.4)

    messages = ["", "You feel thirsty.", "You're starving for water.", "You're gonna die of thirst."]
    labels = ["quenched", "thirsty", "parched", "dying of thirst"]

class TirednessManager(MetabolismHandler):
    def __init__(self, obj):
        super().__init__(obj, 'tiredness')

    messages = ["", "You feel tired.", "You are exhausted.", "You're about to collapse."]
    labels = ["rested", "tired", "exhausted", "about to collapse"]

    def tick(self):
        if self.obj.is_resting:
            recovery = 1 + self.value / 20
            self.decrease(recovery)
        else:
            self.increase()

class MetabolismMixin:
    """Mixin for managing metabolism of a living object."""

    metabolism = AttributeProperty(default=1.0, category="metabolism")

    @lazy_property
    def hunger(self):
        return HungerManager(self)

    @lazy_property
    def thirst(self):
        return ThirstManager(self)

    @lazy_property
    def tiredness(self):
        return TirednessManager(self)

    @property
    def metabolism_handlers(self):
        return [self.hunger, self.thirst, self.tiredness]

    @property
    def is_resting(self) -> bool:
        return self.tags.has("resting", category="living_state")

    @property
    def metabolism_interval(self) -> int:
        return int(600 / self.metabolism)

    def stop_resting(self):
        self.tags.remove("resting", category="living_state")

    def start_resting(self):
        self.tags.add("resting", category="living_state")

    def reset_survival_stats(self):
        for handler in self.metabolism_handlers:
            handler.reset()
        self.stop_resting()

    def start_metabolism_script(self) -> None:
        existing = self.scripts.get("metabolism_script")
        if existing:
            script = existing[0]
            if not script.is_active:
                script.start()
            return
        else:
            script = self.scripts.add(
                "world.living.metabolism.MetabolismScript",
                key="metabolism_script",
            )

    def stop_metabolism_script(self) -> None:
        for script in self.scripts.get("metabolism_script"):
            script.stop()

    def at_init(self):
        super().at_init()
        self.start_metabolism_script()

    def die(self):
        getattr(super(), "die", null_func)()
        self.stop_resting()
        self.stop_metabolism_script()

    def revive(self):
        getattr(super(), "revive", null_func)()
        self.start_metabolism_script()

    def update_living_status(self):
        if any(handler.value >= 100 for handler in self.metabolism_handlers):
            self.die()

    def eat(self, food, calories):
        self.hunger.decrease(calories)

    def drink(self, liquid):
        hydration = liquid.weight.value / 50
        liquid.delete()
        self.thirst.decrease(hydration)

class MetabolismScript(DefaultScript):
    """Regularly increase hunger, thirst and tiredness on a living object."""

    def at_script_creation(self):
        """Called once when first created."""
        self.key = "metabolism_script"
        self.persistent = True
        self.interval = self.obj.metabolism_interval

    def at_repeat(self):
        """Increase hunger, thirst and tiredness each tick."""
        if self.obj.is_dead:
            return
        for handler in self.obj.metabolism_handlers:
            handler.tick()
        # update interval in case metabolism changed
        self.interval = self.obj.metabolism_interval
