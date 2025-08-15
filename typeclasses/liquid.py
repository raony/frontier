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

    def _get_fill_state(self) -> str:
        """Return a short text describing how full the container is."""
        if self.db.is_water_source:
            return "full"

        capacity = self.db.liquid_capacity or 0
        amount = self.db.liquid_amount or 0
        if capacity <= 0 or amount <= 0:
            return "empty"

        ratio = amount / capacity
        if ratio < 0.15:
            return "almost empty"
        if ratio < 0.375:
            return "1/4 full"
        if ratio < 0.625:
            return "1/2 full"
        if ratio < 0.875:
            return "3/4 full"
        if ratio < 1:
            return "almost full"
        return "full"

    def get_display_desc(self, looker, **kwargs):
        """Return description including the container fill state."""
        desc = super().get_display_desc(looker, **kwargs)
        fill_state = self._get_fill_state()
        if desc:
            return f"{desc} It is {fill_state}."
        return f"It is {fill_state}."

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
        if hasattr(drinker, "decrease_thirst"):
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

    def fill_from_container(self, source, filler=None):
        """Fill this container using another container as the source."""
        if self.db.is_water_source:
            if filler:
                filler.msg(f"You can't fill {self.get_display_name(filler)}.")
            return
        if not utils.inherits_from(source, "typeclasses.liquid.LiquidContainerMixin"):
            if filler:
                filler.msg("You can't fill from that.")
            return
        if not source.has_liquid():
            if filler:
                filler.msg(f"{source.get_display_name(filler)} is empty.")
            return
        if self.has_liquid() and self.get_liquid() != source.get_liquid():
            if filler:
                filler.msg("The liquids don't match.")
            return

        available = (self.db.liquid_capacity or 0) - (self.db.liquid_amount or 0)
        if available <= 0:
            if filler:
                filler.msg(f"{self.get_display_name(filler)} is already full.")
            return

        if source.db.is_water_source:
            transfer = available
        else:
            transfer = min(available, source.get_liquid_amount())
        self.db.liquid = source.get_liquid()
        self.db.liquid_amount = (self.db.liquid_amount or 0) + transfer
        if not source.db.is_water_source:
            source.db.liquid_amount = max((source.db.liquid_amount or 0) - transfer, 0)
            if source.db.liquid_amount == 0:
                source.db.liquid = None

        if filler:
            filler.msg(
                f"You fill {self.get_display_name(filler)} from {source.get_display_name(filler)}."
            )
            location = self.location or filler.location
            if location:
                location.msg_contents(
                    f"{filler.get_display_name(location)} fills {self.get_display_name(location)} from {source.get_display_name(location)}.",
                    exclude=filler,
                )


class LiquidContainer(LiquidContainerMixin, Object):
    """Simple container that starts full of water."""

    weight_default = 150  # Container weight in grams

    def at_object_creation(self):
        super().at_object_creation()
        self.db.liquid_capacity = 100
        self.db.liquid_amount = 100
        if self.db.liquid is None:
            self.db.liquid = "water"
