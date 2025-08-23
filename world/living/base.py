from world.physical.weight import WeightHandler
from world.living.commands import AliveCmdSet
from world.living.metabolism import MetabolismMixin
from world.living.perception import PerceptionMixin
from world.utils import null_func
from evennia.utils.utils import lazy_property


class LivingMixin(MetabolismMixin, PerceptionMixin):
    default_weight = 60000

    @lazy_property
    def weight(self):
        return WeightHandler(self)

    @property
    def is_dead(self) -> bool:
        return self.tags.has("dead", category="living_state")

    def at_object_creation(self):
        super().at_object_creation()
        self.tags.add("living_being", category="living_state")
        self.weight.value = self.default_weight

    def load_cmdset(self):
        getattr(super(), "load_cmdset", null_func)()

        if self.cmdset.has(AliveCmdSet):
            return

        self.cmdset.add(AliveCmdSet, persistent=True)

    def clear_cmdset(self):
        getattr(super(), "clear_cmdset", null_func)()

        self.cmdset.remove(AliveCmdSet)

    def die(self):
        getattr(super(), "die", null_func)()
        self.location.msg_contents(
            "$You() collapse lifelessly.",
            from_obj=self,
        )
        self.tags.add("dead", category="living_state")
        self.clear_cmdset()

    def revive(self):
        getattr(super(), "revive", null_func)()
        self.tags.remove("dead", category="living_state")
        self.load_cmdset()

    def reset_and_revive(self):
        self.reset_survival_stats()

        if self.is_dead:
            self.revive()