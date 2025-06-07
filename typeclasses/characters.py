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

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()
        self.db.hunger = 0
        self.db.thirst = 0
        self.db.tiredness = 0
        self.db.is_resting = False
        self.db.is_dead = False
        self.db.is_living = True
        self.db.metabolism = 1.0

    def at_object_post_creation(self):
        """Called after initial creation and attribute setup."""
        super().at_object_post_creation()

        self.start_metabolism_script()

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.pk:
            if self.db.hunger is None:
                self.db.hunger = 0.0
            if self.db.thirst is None:
                self.db.thirst = 0.0
            if self.db.tiredness is None:
                self.db.tiredness = 0.0
            if self.db.is_resting is None:
                self.db.is_resting = False
            if self.db.is_dead is None:
                self.db.is_dead = False
        if self.db.is_living:
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
        self.db.is_dead = True
        self.db.is_living = False
        self.db.is_resting = False
        self.stop_metabolism_script()

    # Hunger/thirst/tiredness management helpers
    def _hunger_level(self) -> int:
        """Return the current hunger level step."""
        hunger = self.db.hunger or 0
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
        thirst = self.db.thirst or 0
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
        tiredness = self.db.tiredness or 0
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

    # Hunger/thirst/tiredness management
    def increase_hunger(self, amount: float = 0.3) -> None:
        """Increase hunger and check for death."""
        self.db.hunger = (self.db.hunger or 0) + amount
        self._notify_hunger()
        self.update_living_status()

    def decrease_hunger(self, amount: float = 1) -> None:
        """Decrease hunger, not going below zero."""
        self.db.hunger = max((self.db.hunger or 0) - amount, 0)
        self._notify_hunger()
        self.update_living_status()

    def increase_thirst(self, amount: float = 1.4) -> None:
        """Increase thirst and check for death."""
        self.db.thirst = (self.db.thirst or 0) + amount
        self._notify_thirst()
        self.update_living_status()

    def decrease_thirst(self, amount: float = 1) -> None:
        """Decrease thirst, not going below zero."""
        self.db.thirst = max((self.db.thirst or 0) - amount, 0)
        self._notify_thirst()
        self.update_living_status()

    def increase_tiredness(self, amount: float = 0.5) -> None:
        """Increase tiredness and check for death."""
        self.db.tiredness = (self.db.tiredness or 0) + amount
        self._notify_tiredness()
        self.update_living_status()

    def decrease_tiredness(self, amount: float = 1) -> None:
        """Decrease tiredness, not going below zero."""
        self.db.tiredness = max((self.db.tiredness or 0) - amount, 0)
        self._notify_tiredness()
        self.update_living_status()

    def update_living_status(self) -> None:
        """Check if this entity should die based on vital stats."""
        if self.db.is_dead:
            return
        if (
            (self.db.hunger or 0) >= 100
            or (self.db.thirst or 0) >= 100
            or (self.db.tiredness or 0) >= 100
        ):
            self.at_death()

    # Metabolism script management
    def get_metabolism_interval(self) -> float:
        """Return real-time seconds per metabolism tick.

        The metabolism rate increases with tiredness so that higher
        tiredness results in more frequent metabolism ticks.
        """
        tiredness = self.db.tiredness or 0
        metabolism = 1 + (tiredness / 50)
        return 600 / metabolism

    def start_metabolism_script(self) -> None:
        """Start or update the metabolism script if needed."""
        if not self.db.is_living:
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

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.db.is_dead:
            self.at_death()
        else:
            self.cmdset.remove(DeadCmdSet)
        self.update_living_status()

    def at_death(self):
        """Handle character-specific death effects."""
        super().at_death()
        self.cmdset.add(DeadCmdSet, permanent=True)
