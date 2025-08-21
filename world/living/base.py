from commands.default_cmdsets import AliveCmdSet
from typeclasses.objects import WeightMixin
from world.living.metabolism import MetabolismMixin
from world.living.perception import PerceptionMixin
from world.utils import null_func


class LivingMixin(MetabolismMixin, PerceptionMixin, WeightMixin):
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

        self.cmdset.add(AliveCmdSet, persistent=True)

    def die(self):
        getattr(super(), "die", null_func)()
        self.location.msg_contents(
            "$You() collapse lifelessly.",
            from_obj=self,
        )
        self.tags.add("dead", category="living_state")
        self.cmdset.clear()
        self.cmdset.remove_default()

    def revive(self):
        getattr(super(), "revive", null_func)()
        self.tags.remove("dead", category="living_state")
        self.load_cmdset()

    def reset_and_revive(self):
        self.reset_survival_stats()

        if self.is_dead:
            self.revive()