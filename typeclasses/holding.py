"""Holding system for game entities."""

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


class HoldableMixin:
    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add("holdable", category="holding")

class HoldableItem(HoldableMixin, Object):
    """Base typeclass for items that can be held in hands."""
    pass

class HeldItemsHandler:
    def __init__(self, holder: Object):
        self.holder = holder

    @property
    def slots(self) -> list[Tag]:
        return self.holder.tags.get(category="holding_slot", return_list=True, return_tagobj=True)

    @property
    def used_slots(self) -> list[Tag]:
        return [item.tags.get(category="holding_slot", return_tagobj=True) for item in self.all]

    @property
    def available_slots(self) -> list[Tag]:
        return [slot for slot in self.slots if slot not in self.used_slots]

    @property
    def all(self) -> list[Object]:
        return [obj for obj in self.holder.contents if obj.tags.has("held", category="holding")]

    def _get_slot(self, slot_key: str) -> Tag:
        return next((slot for slot in self.slots if slot.db_key == slot_key), None)

    def add(self, item: Object, slot_key: str=None) -> bool:
        if slot_key is None:
            if not self.available_slots:
                raise NoSlotsError
            slot = self.available_slots[0]
        else:
            slot = self._get_slot(slot_key)
            if not slot:
                raise InvalidSlotError
            if slot in self.used_slots:
                raise AlreadyHoldingError

        if item.location != self.holder:
            raise NotInInventoryError

        if not item.tags.has("holdable", category="holding"):
            raise NotHoldableError

        if item.tags.has(slot.db_key, category="holding_slot"):
            return False

        item.tags.remove(slot.db_key, category="holding_slot")
        item.tags.add(slot.db_key, category="holding_slot")
        item.tags.add("held", category="holding")
        return slot.db_data or slot.db_key

    def remove(self, item: Object) -> bool:
        if not item or item.location != self.holder:
            return False

        if item.tags.has("held", category="holding"):
            item.tags.remove("held", category="holding")
            item.tags.remove(category="holding_slot")
            return True
        return False

class HolderMixin:
    """Mixin for entities that can hold objects in their hands."""

    @lazy_property
    def held_items(self) -> HeldItemsHandler:
        return HeldItemsHandler(self)

    def at_object_post_creation(self):
        super().at_object_post_creation()
        self.tags.add('main', category="holding_slot", data="main hand")
        self.tags.add('off', category="holding_slot", data="off hand")

    def at_pre_object_leave(self, obj, target_location, **kwargs):
        self.held_items.remove(obj)
        return super().at_pre_object_leave(obj, target_location, **kwargs)