"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia import AttributeProperty

from commands.dead_cmdset import DeadCmdSet
from commands.default_cmdsets import AliveCmdSet

from .objects import ObjectParent


class LivingMixin:
    """Common functionality for all living entities."""

    is_pc = False

    hunger = AttributeProperty(default=0.0)
    thirst = AttributeProperty(default=0.0)
    tiredness = AttributeProperty(default=0.0)
    is_resting = AttributeProperty(default=False)
    is_dead = AttributeProperty(default=False)
    is_living = AttributeProperty(default=True)
    metabolism = AttributeProperty(default=1.0)

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()
        # Attribute defaults are handled by AttributeProperty

    def at_object_post_creation(self):
        """Called after initial creation and attribute setup."""
        super().at_object_post_creation()

        self.start_metabolism_script()

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.pk and getattr(self._state, "db", None):
            if self.is_living:
                self.start_metabolism_script()
            else:
                self.stop_metabolism_script()

    def at_death(self):
        """Handle death of this entity."""
        if self.location:
            self.location.msg_contents(
                "$You() collapse lifelessly.",
                from_obj=self,
            )
        self.is_dead = True
        self.is_living = False
        self.is_resting = False
        self.stop_metabolism_script()
        # Remove alive-only commands and add dead cmdset
        self.cmdset.remove(AliveCmdSet)
        self.cmdset.add(DeadCmdSet, permanent=True)

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

    # Hunger/thirst/tiredness management
    def increase_hunger(self, amount: float = 0.3) -> None:
        """Increase hunger and check for death."""
        self.hunger = (self.hunger or 0) + amount
        self._notify_hunger()
        self.update_living_status()

    def decrease_hunger(self, amount: float = 1) -> None:
        """Decrease hunger, not going below zero."""
        self.hunger = max((self.hunger or 0) - amount, 0)
        self._notify_hunger()
        self.update_living_status()

    def increase_thirst(self, amount: float = 1.4) -> None:
        """Increase thirst and check for death."""
        self.thirst = (self.thirst or 0) + amount
        self._notify_thirst()
        self.update_living_status()

    def decrease_thirst(self, amount: float = 1) -> None:
        """Decrease thirst, not going below zero."""
        self.thirst = max((self.thirst or 0) - amount, 0)
        self._notify_thirst()
        self.update_living_status()

    def increase_tiredness(self, amount: float = 0.5) -> None:
        """Increase tiredness and check for death."""
        self.tiredness = (self.tiredness or 0) + amount
        self._notify_tiredness()
        self.update_living_status()

    def decrease_tiredness(self, amount: float = 1) -> None:
        """Decrease tiredness, not going below zero."""
        self.tiredness = max((self.tiredness or 0) - amount, 0)
        self._notify_tiredness()
        self.update_living_status()

    def update_living_status(self) -> None:
        """Check if this entity should die based on vital stats."""
        if self.is_dead:
            return
        if (
            (self.hunger or 0) >= 100
            or (self.thirst or 0) >= 100
            or (self.tiredness or 0) >= 100
        ):
            self.at_death()

    # Metabolism script management
    def get_metabolism_interval(self) -> float:
        """Return real-time seconds per metabolism tick based on metabolism.

        Uses the Character Attribute `metabolism` (AttributeProperty / self.db.metabolism).
        A higher metabolism value means more frequent ticks (shorter interval).
        """
        value = self.metabolism if hasattr(self, "metabolism") else 1.0
        try:
            effective = float(value)
        except (TypeError, ValueError):
            effective = 1.0
        # Avoid division by zero and overly fast ticking
        effective = max(effective, 0.1)
        return 600 / effective

    def start_metabolism_script(self) -> None:
        """Start or update the metabolism script if needed."""
        if not self.is_living:
            return
        existing = self.scripts.get("metabolism_script")
        interval = self.get_metabolism_interval()
        if existing:
            script = existing[0]
            script.interval = interval
            if not script.is_active:
                script.start()
        else:
            script = self.scripts.add(
                "typeclasses.scripts.MetabolismScript",
                key="metabolism_script",
            )
            if script:
                script.interval = interval
                script.persistent = True

    def stop_metabolism_script(self) -> None:
        """Stop the metabolism script if it exists."""
        for script in self.scripts.get("metabolism_script"):
            script.stop()
            script.delete()


class Character(LivingMixin, ObjectParent, DefaultCharacter):
    """Represents the in-game character entity.

    Three persistent Attributes are introduced on all characters:
    ``hunger``, ``thirst`` and ``tiredness``. They are integers tracking
    how hungry, thirsty or tired a character is. Newly created characters
    start at ``0`` for all values.
    """

    is_pc = True

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()

    def at_pre_move(self, destination, **kwargs):
        """Prevent dead characters from moving under their own power."""
        if self.is_dead:
            self.msg("You are dead and cannot move.")
            return False
        return super().at_pre_move(destination, **kwargs)

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.is_dead:
            self.cmdset.remove(AliveCmdSet)
            self.cmdset.add(DeadCmdSet, permanent=True)
        else:
            self.cmdset.remove(DeadCmdSet)
            self.cmdset.add(AliveCmdSet, permanent=True)
        self.update_living_status()

    def at_death(self):
        """Handle character-specific death effects."""
        super().at_death()
        self.cmdset.remove(AliveCmdSet)
        self.cmdset.add(DeadCmdSet, permanent=True)
