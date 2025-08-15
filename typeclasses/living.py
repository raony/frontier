"""Living/death state management for game entities."""

from evennia import AttributeProperty
from commands.default_cmdsets import AliveCmdSet
from commands.dead_cmdset import DeadCmdSet


class LivingStateMixin:
    """Mixin for managing living/dead state using additive tags.

    This approach uses two tags:
    - "living_being": indicates the object is a living entity
    - "dead": indicates the living being is dead
    
    States:
    - Alive: has "living_being" tag, does NOT have "dead" tag
    - Dead: has both "living_being" AND "dead" tags
    - Not living: has neither tag
    """

    def set_living_state(self, alive: bool):
        """Set living state using additive tags."""
        # Ensure living_being tag exists (all characters are living beings)
        if not self.tags.has("living_being", category="living_state"):
            self.tags.add("living_being", category="living_state")
        
        if alive:
            # Alive: remove dead tag
            self.tags.remove("dead", category="living_state")
        else:
            # Dead: add dead tag
            self.tags.add("dead", category="living_state")

    def is_living_tag(self) -> bool:
        """Check if character is alive using tags."""
        # Alive = has living_being tag AND does NOT have dead tag
        return (self.tags.has("living_being", category="living_state") and
                not self.tags.has("dead", category="living_state"))

    def is_dead_tag(self) -> bool:
        """Check if character is dead using tags."""
        # Dead = has living_being tag AND has dead tag
        return (self.tags.has("living_being", category="living_state") and
                self.tags.has("dead", category="living_state"))

    def is_living_being_tag(self) -> bool:
        """Check if character is a living being (alive or dead)."""
        return self.tags.has("living_being", category="living_state")

    def is_living_state(self) -> bool:
        """Check if character is living (tag-based)."""
        return self.is_living_tag()

    def is_dead_state(self) -> bool:
        """Check if character is dead (tag-based)."""
        return self.is_dead_tag()

    def is_living(self) -> bool:
        """Check if character is living (tag-based)."""
        return self.is_living_tag()

    def is_dead(self) -> bool:
        """Check if character is dead (tag-based)."""
        return self.is_dead_tag()

    def at_object_creation(self):
        """Ensure consistent initial living state."""
        try:
            super().at_object_creation()
        except Exception:
            pass
        # Set default living state if none exists
        if not self.tags.has("living_being", category="living_state"):
            self.tags.add("living_being", category="living_state")


class LivingMixin(LivingStateMixin):
    """Mixin for living entities with metabolism and survival needs."""

    # Survival attributes
    hunger = AttributeProperty(default=0.0)
    thirst = AttributeProperty(default=0.0)
    tiredness = AttributeProperty(default=0.0)
    is_resting = AttributeProperty(default=False)
    metabolism = AttributeProperty(default=1.0)
    light_threshold = AttributeProperty(default=20)

    def at_death(self):
        """Handle death of this entity."""
        if self.location:
            self.location.msg_contents(
                "$You() collapse lifelessly.",
                from_obj=self,
            )
        # Set living state using tags
        self.set_living_state(False)  # This sets dead tag
        self.is_resting = False
        self.stop_metabolism_script()
        # Remove alive-only commands and add dead cmdset
        self.cmdset.remove(AliveCmdSet)
        self.cmdset.add(DeadCmdSet, persistent=True)

    def revive(self):
        """Revive this entity from death."""
        # Use the same revive logic as @revive command
        self.set_living_state(True)
        self.is_resting = False
        self.start_metabolism_script()
        # Remove dead cmdset and add alive cmdset
        self.cmdset.remove(DeadCmdSet)
        self.cmdset.add(AliveCmdSet, persistent=True)

    def reset_survival_stats(self):
        """Reset all survival stats to 0 and clear message levels."""
        self.hunger = 0
        self.thirst = 0
        self.tiredness = 0
        self.is_resting = False
        
        # Clear threshold message trackers
        if hasattr(self, "ndb"):
            self.ndb.hunger_msg_level = 0
            self.ndb.thirst_msg_level = 0
            self.ndb.tiredness_msg_level = 0

    def reset_and_revive(self):
        """Reset survival stats and revive if dead."""
        self.reset_survival_stats()
        
        if self.is_dead():
            self.revive()
            return "You have been revived and your needs are reset."
        else:
            if hasattr(self, "start_metabolism_script"):
                self.start_metabolism_script()
            return "Your needs are reset and you feel refreshed."

    # Hunger/thirst/tiredness management helpers
    def _hunger_level(self) -> int:
        """Return the current hunger level step."""
        hunger = self.hunger or 0
        if hunger >= 60:
            return 3
        if hunger >= 30:
            return 2
        if hunger >= 7:
            return 1
        return 0

    def _notify_hunger(self) -> None:
        """Send hunger warning messages when levels change."""
        level = self._hunger_level()
        last = getattr(self.ndb, "hunger_msg_level", None)
        if level != last:
            if level == 1:
                self.msg("You feel hungry.")
            elif level == 2:
                self.msg("You're starving.")
            elif level == 3:
                self.msg("You're gonna die.")
            self.ndb.hunger_msg_level = level

    def _thirst_level(self) -> int:
        """Return the current thirst level step."""
        thirst = self.thirst or 0
        if thirst >= 60:
            return 3
        if thirst >= 30:
            return 2
        if thirst >= 7:
            return 1
        return 0

    def _notify_thirst(self) -> None:
        """Send thirst warning messages when levels change."""
        level = self._thirst_level()
        last = getattr(self.ndb, "thirst_msg_level", None)
        if level != last:
            if level == 1:
                self.msg("You feel thirsty.")
            elif level == 2:
                self.msg("You're starving for water.")
            elif level == 3:
                self.msg("You're gonna die of thirst.")
            self.ndb.thirst_msg_level = level

    def _tiredness_level(self) -> int:
        """Return the current tiredness level step."""
        tiredness = self.tiredness or 0
        if tiredness >= 60:
            return 3
        if tiredness >= 30:
            return 2
        if tiredness >= 7:
            return 1
        return 0

    def _notify_tiredness(self) -> None:
        """Send tiredness warning messages when levels change."""
        level = self._tiredness_level()
        last = getattr(self.ndb, "tiredness_msg_level", None)
        if level != last:
            if level == 1:
                self.msg("You feel tired.")
            elif level == 2:
                self.msg("You are exhausted.")
            elif level == 3:
                self.msg("You're about to collapse.")
            self.ndb.tiredness_msg_level = level

    # Public-facing label helpers
    def get_hunger_label(self) -> str:
        """Return a user-facing hunger label without numbers."""
        level = self._hunger_level()
        return ["sated", "hungry", "starving", "starving to death"][level]

    def get_thirst_label(self) -> str:
        """Return a user-facing thirst label without numbers."""
        level = self._thirst_level()
        return ["quenched", "thirsty", "parched", "dying of thirst"][level]

    def get_tiredness_label(self) -> str:
        """Return a user-facing tiredness label without numbers."""
        level = self._tiredness_level()
        return ["rested", "tired", "exhausted", "about to collapse"][level]

    def update_living_status(self) -> None:
        """Check if this entity should die based on vital stats."""
        if self.is_dead():
            return
        if (
            (self.hunger or 0) >= 100
            or (self.thirst or 0) >= 100
            or (self.tiredness or 0) >= 100
        ):
            self.at_death()

    # Metabolism API
    def get_metabolism_interval(self) -> int:
        """Return metabolism tick interval in seconds."""
        try:
            metabolism = float(getattr(self, "metabolism", 1.0) or 1.0)
            # Base interval is 60 seconds, modified by metabolism rate
            return max(10, int(60 / metabolism))
        except Exception:
            return 60

    def start_metabolism_script(self) -> None:
        """Start the metabolism script if not already running."""
        existing = self.scripts.get("metabolism_script")
        if existing:
            script = existing[0]
            if not script.is_active:
                script.start()
            return
        script = self.scripts.add(
            "typeclasses.scripts.MetabolismScript",
            key="metabolism_script",
        )
        if script:
            script.interval = self.get_metabolism_interval()
            script.persistent = True

    def stop_metabolism_script(self) -> None:
        """Stop and remove the metabolism script."""
        for script in self.scripts.get("metabolism_script"):
            script.stop()
            script.delete()

    # Metabolism stat increase methods
    def increase_hunger(self) -> None:
        """Increase hunger by metabolism rate."""
        self.hunger = min(100, (self.hunger or 0) + self.metabolism)
        self._notify_hunger()

    def increase_thirst(self) -> None:
        """Increase thirst by metabolism rate."""
        self.thirst = min(100, (self.thirst or 0) + self.metabolism)
        self._notify_thirst()

    def increase_tiredness(self) -> None:
        """Increase tiredness by metabolism rate."""
        self.tiredness = min(100, (self.tiredness or 0) + self.metabolism)
        self._notify_tiredness()
