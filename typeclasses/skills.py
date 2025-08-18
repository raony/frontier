"""Dynamic Skill typeclass and utilities.

Skills are dynamic in-game objects so builders can create new skills without
reloading the server. Characters store their personal skill levels as
Attributes (a mapping from skill keys to level labels).
"""

from evennia import AttributeProperty
from evennia.objects.objects import DefaultObject


class SkillableMixin:
    """Mixin for entities that can have skills.

    This mixin provides skill management functionality for any object that
    needs to track skill levels. Skills are stored as a mapping from skill
    keys to level labels.
    """

    # Skills stored as mapping {skill_key: level_label}
    skills = AttributeProperty(default=dict)

    # Valid skill levels
    VALID_SKILL_LEVELS = {"untrained", "novice", "journeyman", "master"}

    def get_skill_level_label(self, skill_key: str) -> str:
        """Return the textual skill level for a given skill key.

        Levels are textual among {untrained, novice, journeyman, master}. Defaults to untrained.
        """
        skills_map = self.skills or {}
        level = (skills_map.get(skill_key) or "untrained").lower()
        return level if level in self.VALID_SKILL_LEVELS else "untrained"

    def set_skill_level_label(self, skill_key: str, level_label: str) -> None:
        """Set the textual skill level for a given skill key."""
        if level_label not in self.VALID_SKILL_LEVELS:
            raise ValueError("Invalid skill level label")
        skills_map = self.skills or {}
        skills_map[skill_key] = level_label
        self.skills = skills_map


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
