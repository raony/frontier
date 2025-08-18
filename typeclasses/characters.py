"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent
from .equipment import WearerMixin
from .living import LivingMixin
from .holding import HolderMixin


class Character(LivingMixin, HolderMixin, WearerMixin, ObjectParent, DefaultCharacter):
    """Represents the in-game character entity.

    Three persistent Attributes are introduced on all characters:
    ``hunger``, ``thirst`` and ``tiredness``. They are integers tracking
    how hungry, thirsty or tired a character is. Newly created characters
    start at ``0`` for all values.
    """

    is_pc = True

    def get_tag_objs(self, *args, **kwargs):
        return self.tags.get(*args, **kwargs, return_tagobj=True)

    def at_pre_move(self, destination, **kwargs):
        """Prevent dead characters from moving under their own power."""
        if self.is_dead():
            self.msg("You are dead and cannot move.")
            return False
        return super().at_pre_move(destination, **kwargs)

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.is_dead():
            from commands.default_cmdsets import AliveCmdSet
            from commands.dead_cmdset import DeadCmdSet
            self.cmdset.remove(AliveCmdSet)
            self.cmdset.add(DeadCmdSet, persistent=True)
        else:
            from commands.default_cmdsets import AliveCmdSet
            from commands.dead_cmdset import DeadCmdSet
            self.cmdset.remove(DeadCmdSet)
            self.cmdset.add(AliveCmdSet, persistent=True)
        self.update_living_status()

    def at_death(self):
        """Handle character-specific death effects."""
        super().at_death()
        from commands.default_cmdsets import AliveCmdSet
        from commands.dead_cmdset import DeadCmdSet
        self.cmdset.remove(AliveCmdSet)
        self.cmdset.add(DeadCmdSet, persistent=True)

    # --- Perception / Look -------------------------------------------------
    def at_look(self, target, **kwargs):
        """Gate visibility based on ambient light vs character threshold."""
        # Check if we can see details in current light
        if self.location.get_light_level(looker=self) < self.light_threshold:
            return "It's too dark to see anything."
        return super().at_look(target, **kwargs)