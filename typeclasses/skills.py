"""Dynamic Skill typeclass and utilities.

Skills are dynamic in-game objects so builders can create new skills without
reloading the server. Characters store their personal skill levels as
Attributes (a mapping from skill keys to level labels).
"""

from evennia.objects.objects import DefaultObject


class Skill(DefaultObject):
    """Represents a globally defined skill.

    Instances of this typeclass act as skill definitions. They should be
    created by builders using a command. Characters then reference skills by
    the skill object's key.
    """

    def at_object_creation(self):
        super().at_object_creation()
        # Mark this object as a skill so we can search for it efficiently
        self.tags.add("skill", category="system")
        # Optional display name (fallback to the object's key)
        if not self.db.display_name:
            self.db.display_name = self.key.title()

    @property
    def display_name(self) -> str:
        return self.db.display_name or self.key
