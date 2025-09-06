"""Holding system for game entities."""

from evennia import AttributeProperty
from evennia.utils.utils import lazy_property
from evennia.help.models import Tag
from world.equipment.commands import HoldCmdSet
from world.utils import null_func

class HoldableMixin:
    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add("holdable", category="holding")

    def get_display_name(self, looker=None, **kwargs):
        name = super().get_display_name(looker, **kwargs)
        if self.tags.has("held", category="holding"):
            name = f"{name} ({self.location.get_display_holding(self)})"
        if self.weight.total > 0 and hasattr(looker, 'holding_strength') and not kwargs.get("command_narration"):
            name = f"{name} {self.get_display_weight(looker)}"
        return name

    def get_display_weight(self, looker, **kwargs):
        if not hasattr(looker, 'holding_strength'):
            return ''
        if self.weight.total <= looker.holding_strength:
            return '░'
        elif self.weight.total <= looker.holding_strength * len(looker.held_items.slots):
            return '▒'
        else:
            return '█'

class HeldItemsHandler:
    def __init__(self, holder):
        self.holder = holder

    @property
    def slots(self) -> list[str]:
        return self.holder.tags.get(category="holding_slot", return_list=True)

    @property
    def used_slots(self) -> list[str]:
        return sum([item.tags.get(category="holding_slot", return_list=True) for item in self.all], [])

    @property
    def available_slots(self) -> list[str]:
        used_slots = self.used_slots
        return [slot for slot in self.slots if slot not in used_slots]

    @property
    def next_available_slot(self) -> Tag:
        return self.available_slots[0] if self.available_slots else None

    @property
    def all(self) -> list:
        return [obj for obj in self.holder.contents if obj.tags.has("held", category="holding")]

    def is_valid_slot(self, slots: list[str]) -> bool:
        return all(slot in self.slots for slot in slots)

    def is_in_inventory(self, item) -> bool:
        return item.location == self.holder

    def is_holdable(self, item) -> bool:
        return item.tags.has("holdable", category="holding")

    def is_too_heavy(self, item, slots: list[str]) -> bool:
        return item.weight.total > len(slots) * self.holder.holding_strength

    def is_already_holding(self, item, slots: list[str]) -> bool:
        return set(slots) == set(self.get_slots_for(item))

    def is_slots_available(self, item, slots: list[str]) -> bool:
        available_slots = self.available_slots + self.get_slots_for(item)
        return all(slot in available_slots for slot in slots)

    def can_hold(self, item, slots: list[str]) -> bool:
        return (
            self.is_valid_slot(slots)
            and self.is_in_inventory(item)
            and self.is_holdable(item)
            and not self.is_too_heavy(item, slots)
            and not self.is_already_holding(item, slots)
            and self.is_slots_available(item, slots)
        )

    def add(self, item, slots: list[str]) -> bool:
        if not self.can_hold(item, slots):
            return False

        item.tags.remove(category="holding_slot")
        item.tags.remove(category="equipment_slot")
        item.tags.remove("equipped", category="equipment")
        for slot in slots:
            item.tags.add(slot, category="holding_slot")
        item.tags.add("held", category="holding")
        return True

    def remove(self, item) -> bool:
        if not item or item.location != self.holder:
            return False

        if item.tags.has("held", category="holding"):
            item.tags.remove("held", category="holding")
            item.tags.remove(category="holding_slot")
            return True
        return False

    def get_slots_for(self, item) -> list[str]:
        return item.tags.get(category="holding_slot", return_list=True)

class HolderMixin:
    """Mixin for entities that can hold objects in their hands."""

    holding_strength = AttributeProperty(default=10000)

    @lazy_property
    def held_items(self) -> HeldItemsHandler:
        return HeldItemsHandler(self)

    def load_cmdset(self):
        getattr(super(), "load_cmdset", null_func)()
        if not self.cmdset.has(HoldCmdSet):
            self.cmdset.add(HoldCmdSet, persistent=True)

    def clear_cmdset(self):
        getattr(super(), "clear_cmdset", null_func)()
        self.cmdset.remove(HoldCmdSet)

    def at_object_post_creation(self):
        super().at_object_post_creation()
        self.tags.add('main hand', category="holding_slot")
        self.tags.add('off hand', category="holding_slot")

    def at_pre_object_leave(self, obj, target_location, **kwargs):
        self.held_items.remove(obj)
        self.equipment.remove(obj)
        return super().at_pre_object_leave(obj, target_location, **kwargs)

    def get_display_holding(self, item) -> str:
        slots = self.held_items.get_slots_for(item)
        if len(slots) == 1:
            return slots[0]
        elif len(slots) == 2:
            return "both hands"