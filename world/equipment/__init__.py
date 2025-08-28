"""
Equipment package for the Frontier MUD game.

This package contains equipment-related systems including:
- Holding system for items that can be held in hands
- Equipment system for wearable items
"""

from .holding import (
    HoldableMixin,
    HeldItemsHandler,
    HolderMixin,
)

from .exceptions import (
    NotInInventoryError,
    NotEquippableError,
    AlreadyEquippedError,
)

from .equipment import (
    EquippableMixin,
    EquipmentHandler,
    WearerMixin,
    EQUIPMENT_SLOTS,
    normalize_slot,
)

__all__ = [
    'HoldableMixin',
    'HeldItemsHandler',
    'HolderMixin',
    'NotInInventoryError',
    'NotEquippableError',
    'AlreadyEquippedError',
    'EquippableMixin',
    'EquipmentHandler',
    'WearerMixin',
    'EQUIPMENT_SLOTS',
    'normalize_slot',
]
