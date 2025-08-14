"""
Concrete equippable item base classes per slot.

Use these typeclasses to create items in-game directly, e.g.:
  @create "Leather Cap":typeclasses.items.HeadItem
Then edit its desc/aliases etc as usual.
"""

from .objects import Object, LightSourceMixin
from .equipment import (
    EquippableHead,
    EquippableBody,
    EquippableLegs,
    EquippableWaist,
    EquippableHands,
    EquippableFeet,
)


class HeadItem(EquippableHead, Object):
    """Base typeclass for items that equip to the head slot."""


class BodyItem(EquippableBody, Object):
    """Base typeclass for items that equip to the body slot."""


class LegsItem(EquippableLegs, Object):
    """Base typeclass for items that equip to the legs slot."""


class WaistItem(EquippableWaist, Object):
    """Base typeclass for items that equip to the waist slot."""


class HandsItem(EquippableHands, Object):
    """Base typeclass for items that equip to the hands slot."""


class FeetItem(EquippableFeet, Object):
    """Base typeclass for items that equip to the feet slot."""


# --- Holdable items -----------------------------------------------------------

class HoldableMixin:
    """Mixin for items that can be held in hands (not worn).

    On creation, sets a persistent attribute `db.is_holdable = True` so builders
    can mark holdables and commands can validate items for holding.
    """

    def at_object_creation(self):
        try:
            super().at_object_creation()  # type: ignore[misc]
        except Exception:
            pass
        self.db.is_holdable = True


class HoldableItem(HoldableMixin, Object):
    """Base typeclass for simple items intended to be held in hand."""


class Torch(HoldableMixin, LightSourceMixin, Object):
    """A simple handheld torch that emits light.

    This torch provides enough light to see in dark places when present in
    a room or when held/carried by someone in the room.
    """

    light_level_default = 40
