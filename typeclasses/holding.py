"""Holding system for game entities."""

from django.utils import tree
from evennia import AttributeProperty
from evennia.utils.utils import lazy_property
from evennia.help.models import Tag
from .objects import Object

class NoSlotsError(Exception):
    """Exception raised when no slots are available."""
    pass

class NotInInventoryError(Exception):
    """Exception raised when an item is not in the inventory."""
    pass

class NotHoldableError(Exception):
    """Exception raised when an item is not holdable."""
    pass

class InvalidSlotError(Exception):
    """Exception raised when an invalid slot is provided."""
    pass

class AlreadyHoldingError(Exception):
    """Exception raised when the slot is already holding an item."""
    pass

class TooHeavyError(Exception):
    """Exception raised when an item is too heavy to hold."""
    pass


class HoldableMixin:
    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add("holdable", category="holding")

    def get_display_name(self, looker=None, **kwargs):
        name = super().get_display_name(looker, **kwargs)
        if self.tags.has("held", category="holding"):
            name = f"{name} ({self.location.get_display_holding(self)})"
        if self.total_weight > 0:
            name = f"{name} {self.get_display_weight(looker)}"
        return name

    def get_display_weight(self, looker, **kwargs):
        if not hasattr(looker, 'holding_strength'):
            return ''
        if self.total_weight <= looker.holding_strength:
            return '░'
        elif self.total_weight <= looker.holding_strength * len(looker.held_items.slots):
            return '▒'
        else:
            return '█'

class HoldableItem(HoldableMixin, Object):
    """Base typeclass for items that can be held in hands."""
    pass

class HeldItemsHandler:
    def __init__(self, holder: Object):
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
    def all(self) -> list[Object]:
        return [obj for obj in self.holder.contents if obj.tags.has("held", category="holding")]

    def add(self, item: Object, slots: list[str]) -> bool:
        valid_slots = self.slots
        if not all(slot in valid_slots for slot in slots):
            raise InvalidSlotError

        if item.location != self.holder:
            raise NotInInventoryError

        if not item.tags.has("holdable", category="holding"):
            raise NotHoldableError

        # Check if item is too heavy for the available slots
        total_weight = item.total_weight
        max_weight = len(slots) * self.holder.holding_strength
        if total_weight > max_weight:
            raise TooHeavyError

        current_slots = self.get_slots_for(item)
        if set(current_slots) == set(slots):
            return False

        used_slots = [slot for slot in self.used_slots if slot not in current_slots]
        if any(slot in used_slots for slot in slots):
            raise AlreadyHoldingError

        item.tags.remove(category="holding_slot")
        for slot in slots:
            item.tags.add(slot, category="holding_slot")
        item.tags.add("held", category="holding")
        return True

    def remove(self, item: Object) -> bool:
        if not item or item.location != self.holder:
            return False

        if item.tags.has("held", category="holding"):
            item.tags.remove("held", category="holding")
            item.tags.remove(category="holding_slot")
            return True
        return False

    def get_slots_for(self, item: Object) -> list[str]:
        return item.tags.get(category="holding_slot", return_list=True)

class HolderMixin:
    """Mixin for entities that can hold objects in their hands."""

    holding_strength = AttributeProperty(default=10000)

    @lazy_property
    def held_items(self) -> HeldItemsHandler:
        return HeldItemsHandler(self)

    def at_object_post_creation(self):
        super().at_object_post_creation()
        self.tags.add('main', category="holding_slot", data="main hand")
        self.tags.add('off', category="holding_slot", data="off hand")

    def at_pre_object_leave(self, obj, target_location, **kwargs):
        self.held_items.remove(obj)
        self.equipment.remove(obj)
        return super().at_pre_object_leave(obj, target_location, **kwargs)

    def get_display_holding(self, item: Object) -> str:
        slots = self.held_items.get_slots_for(item)
        if len(slots) == 1:
            return Tag.objects.get(db_key=slots[0], db_category="holding_slot").db_data
        elif len(slots) == 2:
            return "both hands"