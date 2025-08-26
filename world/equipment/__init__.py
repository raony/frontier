"""
Equipment package for the Frontier MUD game.

This package contains equipment-related systems including:
- Holding system for items that can be held in hands
- Equipment system for wearable items
"""

from .holding import (
    HoldableMixin,
    HoldableItem,
    HeldItemsHandler,
    HolderMixin,
    NoSlotsError,
    NotInInventoryError,
    NotHoldableError,
    InvalidSlotError,
    AlreadyHoldingError,
    TooHeavyError,
)

__all__ = [
    'HoldableMixin',
    'HoldableItem',
    'HeldItemsHandler',
    'HolderMixin',
    'NoSlotsError',
    'NotInInventoryError',
    'NotHoldableError',
    'InvalidSlotError',
    'AlreadyHoldingError',
    'TooHeavyError',
]
