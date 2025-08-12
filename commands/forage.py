"""Foraging command using character skill + room resources."""

from random import random
from typing import Optional

from evennia import create_object

from .command import Command


def _get_skill_level_value(level_label: str) -> int:
    label = (level_label or "untrained").lower()
    if label.startswith("master"):
        return 3
    if label.startswith("journey") or label.startswith("journeyman"):
        return 2
    if label.startswith("novice"):
        return 1
    return 0  # untrained


def _find_foraging_resource(location) -> Optional[object]:
    if not location:
        return None
    # Search for objects tagged as resource:foraging
    for obj in location.contents:
        if obj.tags.get("resource:foraging", category="system") and not getattr(obj, "is_depleted", False):
            return obj
    return None


class CmdForage(Command):
    """Search the area for edible resources.

    Usage:
      forage
    """

    key = "forage"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not caller.location:
            caller.msg("You are nowhere; there's nothing to forage.")
            return

        resource = _find_foraging_resource(caller.location)
        if not resource or getattr(resource, "is_depleted", False):
            caller.msg("You find nothing edible here.")
            return

        # Determine effective skill
        if hasattr(caller, "get_skill_level_label"):
            level_label = caller.get_skill_level_label("foraging")
        else:
            level_label = "untrained"

        skill_value = _get_skill_level_value(level_label)

        # Resource quality: 1..3
        try:
            quality = max(1, min(int(resource.db.quality or 1), 3))
        except (TypeError, ValueError):
            quality = 1

        # Simple chance and yield logic
        # Base chance increases with skill and resource quality
        # Untrained should be much harder; base chance lower when 0
        base = 0.05 if skill_value == 0 else 0.2
        chance = base + 0.15 * (skill_value - 1) + 0.1 * (quality - 1)
        if random() > chance:
            caller.msg("You search around but fail to find anything this time.")
            return

        # Found something — create a simple food object and reduce abundance
        calories = max(1, 1 + (skill_value - 1) + (quality - 1))
        try:
            item = create_object("typeclasses.food.Food", key="foraged food", location=caller)
            item.db.calories = calories
        except Exception:  # pragma: no cover - safety net
            caller.msg("You would have found something, but it slips through your fingers.")
            return

        # Deplete resource
        try:
            resource.db.abundance = max(int(resource.db.abundance or 1) - 1, 0)
        except (TypeError, ValueError):
            resource.db.abundance = 0

        caller.msg(f"You forage the area and find some food ({calories} calories).")
        if resource.db.abundance <= 0:
            caller.location.msg_contents(
                "The area looks picked clean of edible resources.", exclude=caller
            )
