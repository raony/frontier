"""
Equipment system constants and helpers.

This module centralizes slot definitions to avoid circular imports between
typeclasses and commands.
"""

from typing import Dict, List, Optional


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


def default_equipment_map() -> Dict[str, Optional[int]]:
    """Return a fresh equipment mapping with all slots set to None.

    Values will store the equipped object (Evennia typeclass instance) or None.
    We keep typing as Optional[int] for clarity but store objects.
    """
    return {slot: None for slot in EQUIPMENT_SLOTS}


# --- Item mixins ------------------------------------------------------------

class EquippableBaseMixin:
    """Base mixin for items that can be equipped to a specific slot.

    Subclasses should set class attribute `slot_name` to one of EQUIPMENT_SLOTS.
    This mixin ensures the item reports itself as equipable and sets a helpful
    description for the slot used.
    """

    # Override in subclasses
    slot_name: Optional[str] = None

    def at_object_creation(self):
        # Call parent hooks first
        try:
            super().at_object_creation()  # type: ignore[misc]
        except Exception:
            pass
        slot = normalize_slot(self.slot_name)
        if slot:
            # Store on db so generic Object helper can detect it
            self.db.equipable = slot

    @property
    def equipable_slot(self) -> Optional[str]:
        # Prefer explicit slot_name if valid; fallback to parent implementation
        slot = normalize_slot(self.slot_name)
        if slot:
            return slot
        try:
            return super().equipable_slot  # type: ignore[attr-defined]
        except Exception:
            return None


class EquippableHead(EquippableBaseMixin):
    slot_name = "head"


class EquippableBody(EquippableBaseMixin):
    slot_name = "body"


class EquippableLegs(EquippableBaseMixin):
    slot_name = "legs"


class EquippableWaist(EquippableBaseMixin):
    slot_name = "waist"


class EquippableHands(EquippableBaseMixin):
    slot_name = "hands"


class EquippableFeet(EquippableBaseMixin):
    slot_name = "feet"
