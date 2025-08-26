"""
Equipment system exceptions.

This module centralizes all exceptions used by the equipment and holding systems.
"""


class NotInInventoryError(Exception):
    """Exception raised when an item is not in the inventory."""
    pass


class NotEquippableError(Exception):
    """Exception raised when an item is not equippable."""
    pass


class AlreadyEquippedError(Exception):
    """Exception raised when an item is already equipped."""
    pass
