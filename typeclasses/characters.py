"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """Represents the in-game character entity.

    Two new persistent Attributes are introduced on all characters:
    ``hunger`` and ``thirst``. They are integers tracking how hungry or
    thirsty a character is. Newly created characters start at ``0`` for
    both values.
    """

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()
        self.db.hunger = 0
        self.db.thirst = 0

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.db.hunger is None:
            self.db.hunger = 0
        if self.db.thirst is None:
            self.db.thirst = 0
