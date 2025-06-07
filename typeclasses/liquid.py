"""Liquid container mixin."""

from evennia.utils import utils
from .objects import Object


class LiquidContainerMixin:
    """Mixin for objects that can store a liquid."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.liquid = None
        self.db.liquid_capacity = 1
        self.db.liquid_amount = 0
        self.db.is_water_source = False

    # Helpers
    def has_liquid(self) -> bool:
        """Return True if there is any liquid available."""
        if self.db.is_water_source:
            return True
        return self.db.liquid is not None and (self.db.liquid_amount or 0) > 0

    def get_liquid(self):
        """Return the current liquid stored, or None."""
        return self.db.liquid

    def get_liquid_amount(self) -> int:
        """Return current amount of liquid."""
        if self.db.is_water_source:
            return self.db.liquid_capacity or 0
        return self.db.liquid_amount or 0

    # Actions
    def fill_liquid(self, liquid: str, filler=None):
        """Fill this container with `liquid`."""
        if self.db.is_water_source:
            if filler:
                filler.msg(f"You can't fill {self.get_display_name(filler)}.")
            return
        self.db.liquid = liquid
        self.db.liquid_amount = self.db.liquid_capacity or 0
        if filler:
            filler.msg(f"You fill {self.get_display_name(filler)} with {liquid}.")
            location = self.location or filler.location
            if location:
                location.msg_contents(
                    f"{filler.get_display_name(location)} fills {self.get_display_name(location)} with {liquid}.",
                    exclude=filler,
                )

    def empty_liquid(self, emptier=None):
        """Empty the container."""
        if self.db.is_water_source:
            if emptier:
                emptier.msg(f"You can't empty {self.get_display_name(emptier)}.")
            return
        if not self.has_liquid():
            if emptier:
                emptier.msg(f"{self.get_display_name(emptier)} is already empty.")
            return
        self.db.liquid = None
        self.db.liquid_amount = 0
        if emptier:
            emptier.msg(f"You empty {self.get_display_name(emptier)}.")
            location = self.location or emptier.location
            if location:
                location.msg_contents(
                    f"{emptier.get_display_name(location)} empties {self.get_display_name(location)}.",
                    exclude=emptier,
                )

    def drink_liquid(self, drinker, amount: int = 1):
        """Consume liquid from this container."""
        if not self.has_liquid():
            drinker.msg(f"{self.get_display_name(drinker)} is empty.")
            return
        if utils.inherits_from(drinker, "typeclasses.characters.LivingMixin"):
            drinker.decrease_thirst(20)
        if not self.db.is_water_source:
            self.db.liquid_amount = max((self.db.liquid_amount or 0) - amount, 0)
            if self.db.liquid_amount == 0:
                self.db.liquid = None
        drinker.msg(f"You drink from {self.get_display_name(drinker)}.")
        location = self.location or drinker.location
        if location:
            location.msg_contents(
                f"{drinker.get_display_name(location)} drinks from {self.get_display_name(location)}.",
                exclude=drinker,
            )


class LiquidContainer(LiquidContainerMixin, Object):
    """Simple container that starts full of water."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.liquid_capacity = 100
        self.db.liquid_amount = 100
        if self.db.liquid is None:
            self.db.liquid = "water"
