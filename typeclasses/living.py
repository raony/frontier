"""Living/death state management for game entities."""

from evennia import AttributeProperty
from commands.default_cmdsets import AliveCmdSet
from commands.dead_cmdset import DeadCmdSet
from world.living.metabolism import MetabolismMixin
from world.utils import null_func


class LivingMixin(MetabolismMixin):
    """Mixin for managing living/dead state using additive tags."""

    light_threshold = AttributeProperty(default=20)

    @property
    def is_dead(self) -> bool:
        return self.tags.has("dead", category="living_state")

    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add("living_being", category="living_state")

    def load_cmdset(self):
        getattr(super(), "load_cmdset", null_func)()

        if self.cmdset.has(AliveCmdSet):
            return

        self.cmdset.add(AliveCmdSet)

    def die(self):
        getattr(super(), "die", null_func)()
        self.location.msg_contents(
            "$You() collapse lifelessly.",
            from_obj=self,
        )
        self.tags.add("dead", category="living_state")
        self.cmdset.clear()
        self.cmdset.remove_default()
        self.cmdset.add(DeadCmdSet)

    def revive(self):
        getattr(super(), "revive", null_func)()
        self.tags.remove("dead", category="living_state")
        self.load_cmdset()

    def reset_and_revive(self):
        """Reset survival stats and revive if dead."""
        self.reset_survival_stats()

        if self.is_dead:
            self.revive()
            return "You have been revived and your needs are reset."
        else:
            return "Your needs are reset and you feel refreshed."