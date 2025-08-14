"""
Concrete equippable item base classes per slot.

Use these typeclasses to create items in-game directly, e.g.:
  @create "Leather Cap":typeclasses.items.HeadItem
Then edit its desc/aliases etc as usual.
"""

from .objects import Object
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
