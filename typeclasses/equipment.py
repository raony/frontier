"""
Equipment system constants and helpers.

This module centralizes slot definitions to avoid circular imports between
typeclasses and commands.
"""

from typing import List, Optional
from evennia.utils.utils import lazy_property
from .holding import NotInInventoryError
from .objects import Object

class NotEquippableError(Exception):
    """Exception raised when an item is not equippable."""
    pass

class AlreadyEquippedError(Exception):
    """Exception raised when an item is already equipped."""
    pass

class WrongSlotError(Exception):
    """Exception raised when an item is equipped to the wrong slot."""
    pass


# Canonical equipment slots
EQUIPMENT_SLOTS: List[str] = [
    "head",
    "body",
    "legs",
    "waist",
    "hands",
    "feet",
]


def normalize_slot(slot: Optional[str]) -> Optional[str]:
    """Normalize a slot string to the canonical form.

    Returns None if the input is falsy or not recognized.
    """
    if not slot:
        return None
    value = str(slot).strip().lower()
    return value if value in EQUIPMENT_SLOTS else None


class EquippableMixin:
    """Mixin for items that can be equipped to a specific slot.

    This mixin adds tag-based equipment functionality alongside the existing
    attribute-based system for comparison.
    """

    def at_object_creation(self):
        super().at_object_creation()
        # Add wearable tag for tag-based system
        self.tags.add("equipable", category="equipment")

        # Set the slot tag if slot_name is defined
        if hasattr(self, 'default_slot_name') and self.default_slot_name:
            slot = normalize_slot(self.default_slot_name)
            if slot:
                self.tags.add(slot, category="default_wearing_slot")

    def get_display_name(self, looker=None, **kwargs):
        name = super().get_display_name(looker, **kwargs)
        if self.tags.has("equipable", category="equipment"):
            slot_tags = self.tags.get(category="equipment_slot", return_list=True)
            if slot_tags:
                slot_name = slot_tags[0]  # Get the first slot tag
                return f"{name} ({slot_name})"
        return name


class EquipmentHandler:
    """Handler for managing worn items using tags.

    This provides tag-based equipment management alongside the existing
    attribute-based system for comparison.
    """

    def __init__(self, wearer):
        self.wearer = wearer

    @property
    def slots(self) -> list[str]:
        """Get all available equipment slots."""
        return self.wearer.tags.get(category="equipment_slot", return_list=True)

    @property
    def used_slots(self) -> list[str]:
        """Get all slots that currently have items equipped."""
        used = []
        for obj in self.wearer.contents:
            if obj.tags.has("equipped", category="equipment"):
                slot_tags = obj.tags.get(category="equipment_slot", return_list=True)
                used.extend(slot_tags)
        return used

    @property
    def available_slots(self) -> list[str]:
        """Get all slots that are currently empty."""
        used_slots = self.used_slots
        return [slot for slot in self.slots if slot not in used_slots]

    @property
    def all(self) -> list:
        """Get all currently worn items."""
        return [obj for obj in self.wearer.contents if obj.tags.has("equipped", category="equipment")]

    def get_item_in_slot(self, slot: str) -> Object | None:
        for obj in self.all:
            if obj.tags.has(slot, category="equipment_slot"):
                return obj
        return None

    def add(self, item, slot: str=None) -> bool:
        """Equip an item to a specific slot."""
        if item.location != self.wearer:
            raise NotInInventoryError

        if not item.tags.has("equipable", category="equipment"):
            raise NotEquippableError

        if slot:
            slot = normalize_slot(slot)
        else:
            slot = normalize_slot(item.default_slot_name)

        if item == self.get_item_in_slot(slot):
            return False

        if slot in self.used_slots:
            raise AlreadyEquippedError

        item.tags.remove(category="equipment_slot")
        item.tags.remove(category="holding_slot")
        item.tags.add("equipped", category="equipment")
        item.tags.add(slot, category="equipment_slot")
        return True

    def remove(self, item) -> bool:
        if item.location != self.wearer:
            raise NotInInventoryError

        item.tags.remove(category="equipment_slot")
        item.tags.remove("equipped", category="equipment")
        return True

class WearerMixin:
    """Mixin for objects that can wear items."""

    @lazy_property
    def equipment(self) -> EquipmentHandler:
        return EquipmentHandler(self)

    def at_object_creation(self):
        super().at_object_creation()
        for slot in EQUIPMENT_SLOTS:
            self.tags.add(slot, category="equipment_slot")



# --- Item mixins ------------------------------------------------------------

class EquippableHead(EquippableMixin):
    default_slot_name = "head"


class EquippableBody(EquippableMixin):
    default_slot_name = "body"


class EquippableLegs(EquippableMixin):
    default_slot_name = "legs"


class EquippableWaist(EquippableMixin):
    default_slot_name = "waist"


class EquippableHands(EquippableMixin):
    default_slot_name = "hands"


class EquippableFeet(EquippableMixin):
    default_slot_name = "feet"
