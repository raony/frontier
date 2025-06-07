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
        if self.db.hunger is None:
            self.db.hunger = 0
        if self.db.thirst is None:
            self.db.thirst = 0
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
        self.stop_metabolism_script()

    # Hunger/thirst management
    def increase_hunger(self, amount: int = 1) -> None:
        """Increase hunger and check for death."""
        self.db.hunger = (self.db.hunger or 0) + amount
        self.update_living_status()

    def decrease_hunger(self, amount: int = 1) -> None:
        """Decrease hunger, not going below zero."""
        self.db.hunger = max((self.db.hunger or 0) - amount, 0)
        self.update_living_status()

    def increase_thirst(self, amount: int = 1) -> None:
        """Increase thirst and check for death."""
        self.db.thirst = (self.db.thirst or 0) + amount
        self.update_living_status()

    def decrease_thirst(self, amount: int = 1) -> None:
        """Decrease thirst, not going below zero."""
        self.db.thirst = max((self.db.thirst or 0) - amount, 0)
        self.update_living_status()

    def update_living_status(self) -> None:
        """Check if this entity should die based on hunger or thirst."""
        if self.db.is_dead:
            return
        if (self.db.hunger or 0) >= 100 or (self.db.thirst or 0) >= 100:
            self.at_death()

    # Metabolism script management
    def get_metabolism_interval(self) -> float:
        """Return real-time seconds per hunger tick based on metabolism."""
        metabolism = self.db.metabolism or 1.0
        return 3600 / (6 * metabolism)

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
            self.scripts.add(
                "typeclasses.scripts.MetabolismScript",
                key="metabolism_script",
                interval=interval,
                persistent=True,
            )

    def stop_metabolism_script(self) -> None:
        """Stop the metabolism script if it exists."""
        for script in self.scripts.get("metabolism_script"):
            script.stop()
            script.delete()


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
