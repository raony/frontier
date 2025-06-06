"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from commands.dead_cmdset import DeadCmdSet

from .objects import ObjectParent


class LivingMixin:
    """Common functionality for all living entities."""

    is_pc = False

    def at_death(self):
        """Handle death of this entity."""
        if self.location:
            self.location.msg_contents(
                "$You() collapse lifelessly.",
                from_obj=self,
            )
        self.db.is_dead = True


class Character(LivingMixin, ObjectParent, DefaultCharacter):
    """Represents the in-game character entity.

    Two new persistent Attributes are introduced on all characters:
    ``hunger`` and ``thirst``. They are integers tracking how hungry or
    thirsty a character is. Newly created characters start at ``0`` for
    both values.
    """

    is_pc = True

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()
        self.db.hunger = 0
        self.db.thirst = 0
        self.db.is_dead = False

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.db.hunger is None:
            self.db.hunger = 0
        if self.db.thirst is None:
            self.db.thirst = 0
        if self.db.is_dead is None:
            self.db.is_dead = False
        if self.db.is_dead:
            self.cmdset.add(DeadCmdSet, permanent=True)

    def at_death(self):
        """Handle character-specific death effects."""
        super().at_death()
        self.cmdset.add(DeadCmdSet, permanent=True)
