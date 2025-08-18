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

    def is_living(self) -> bool:
        """Check if character is alive using tags."""
        # Alive = has living_being tag AND does NOT have dead tag
        return (self.tags.has("living_being", category="living_state") and
                not self.tags.has("dead", category="living_state"))

    def is_dead(self) -> bool:
        """Check if character is dead using tags."""
        # Dead = has living_being tag AND has dead tag
        return (self.tags.has("living_being", category="living_state") and
                self.tags.has("dead", category="living_state"))

    def is_living_being(self) -> bool:
        """Check if character is a living being (alive or dead)."""
        return self.tags.has("living_being", category="living_state")

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


    def _switch_command_sets(self, alive: bool):
        """Switch between alive and dead command sets."""
        if alive:
            self.cmdset.remove(DeadCmdSet)
            self.cmdset.add(AliveCmdSet, persistent=True)
        else:
            self.cmdset.remove(AliveCmdSet)
            self.cmdset.add(DeadCmdSet, persistent=True)

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
        # Switch to dead command set
        self._switch_command_sets(False)

    def at_pre_move(self, destination, **kwargs):
        """Prevent dead characters from moving under their own power."""
        if self.is_dead():
            self.msg("You are dead and cannot move.")
            return False
        return super().at_pre_move(destination, **kwargs)

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        self._switch_command_sets(not self.is_dead())
        self.update_living_status()



    def revive(self):
        """Revive this entity from death."""
        # Use the same revive logic as @revive command
        self.set_living_state(True)
        self.is_resting = False
        self.start_metabolism_script()
        # Switch to alive command set
        self._switch_command_sets(True)

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
    def _get_level(self, stat_value: float) -> int:
        """Return the level step for a given stat value."""
        value = stat_value or 0
        if value >= 60:
            return 3
        if value >= 30:
            return 2
        if value >= 7:
            return 1
        return 0

    def _notify_stat_change(self, stat_name: str, level: int, messages: list) -> None:
        """Send notification messages when stat levels change."""
        last = getattr(self.ndb, f"{stat_name}_msg_level", None)
        if level != last:
            if 0 <= level < len(messages):
                self.msg(messages[level])
            setattr(self.ndb, f"{stat_name}_msg_level", level)

    def _hunger_level(self) -> int:
        """Return the current hunger level step."""
        return self._get_level(self.hunger)

    def _notify_hunger(self) -> None:
        """Send hunger warning messages when levels change."""
        level = self._hunger_level()
        messages = ["", "You feel hungry.", "You're starving.", "You're gonna die."]
        self._notify_stat_change("hunger", level, messages)

    def _thirst_level(self) -> int:
        """Return the current thirst level step."""
        return self._get_level(self.thirst)

    def _notify_thirst(self) -> None:
        """Send thirst warning messages when levels change."""
        level = self._thirst_level()
        messages = ["", "You feel thirsty.", "You're starving for water.", "You're gonna die of thirst."]
        self._notify_stat_change("thirst", level, messages)

    def _tiredness_level(self) -> int:
        """Return the current tiredness level step."""
        return self._get_level(self.tiredness)

    def _notify_tiredness(self) -> None:
        """Send tiredness warning messages when levels change."""
        level = self._tiredness_level()
        messages = ["", "You feel tired.", "You are exhausted.", "You're about to collapse."]
        self._notify_stat_change("tiredness", level, messages)

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
        if any((getattr(self, stat, 0) or 0) >= 100 for stat in ["hunger", "thirst", "tiredness"]):
            self.at_death()

    # Metabolism API
    def get_metabolism_interval(self) -> int:
        """Return metabolism tick interval in seconds."""
        try:
            metabolism = float(getattr(self, "metabolism", 1.0) or 1.0)
            # Base interval is 600 seconds, modified by metabolism rate
            return max(10, int(600 / metabolism))
        except Exception:
            return 600

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
    def _increase_stat(self, stat_name: str, amount: float, notify_method) -> None:
        """Increase a stat by amount, not going above 100."""
        current_value = getattr(self, stat_name, 0) or 0
        new_value = min(current_value + amount, 100)
        setattr(self, stat_name, new_value)
        notify_method()

    def increase_hunger(self) -> None:
        """Increase hunger by metabolism rate."""
        self._increase_stat("hunger", self.metabolism, self._notify_hunger)

    def increase_thirst(self) -> None:
        """Increase thirst by metabolism rate."""
        self._increase_stat("thirst", self.metabolism, self._notify_thirst)

    def increase_tiredness(self, amount: float = None) -> None:
        """Increase tiredness by amount or metabolism rate if not specified."""
        if amount is None:
            amount = self.metabolism
        self._increase_stat("tiredness", amount, self._notify_tiredness)

    def _decrease_stat(self, stat_name: str, amount: float, notify_method) -> None:
        """Decrease a stat by amount, not going below zero."""
        current_value = getattr(self, stat_name, 0) or 0
        new_value = max(current_value - amount, 0)
        setattr(self, stat_name, new_value)
        notify_method()
        self.update_living_status()

    def decrease_hunger(self, amount: float = 1.0) -> None:
        """Decrease hunger by amount, not going below zero."""
        self._decrease_stat("hunger", amount, self._notify_hunger)

    def decrease_thirst(self, amount: float = 1.0) -> None:
        """Decrease thirst by amount, not going below zero."""
        self._decrease_stat("thirst", amount, self._notify_thirst)

    def decrease_tiredness(self, amount: float = 1.0) -> None:
        """Decrease tiredness by amount, not going below zero."""
        self._decrease_stat("tiredness", amount, self._notify_tiredness)
