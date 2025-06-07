"""Liquid container mixin."""

from evennia.utils import utils


class LiquidContainerMixin:
    """Mixin for objects that can store a liquid."""

    def at_object_creation(self):
        super().at_object_creation()
        self.db.liquid = None

    def fill_liquid(self, liquid: str, filler=None):
        """Fill this container with `liquid`."""
        self.db.liquid = liquid
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
        if self.db.liquid is None:
            if emptier:
                emptier.msg(f"{self.get_display_name(emptier)} is already empty.")
            return
        self.db.liquid = None
        if emptier:
            emptier.msg(f"You empty {self.get_display_name(emptier)}.")
            location = self.location or emptier.location
            if location:
                location.msg_contents(
                    f"{emptier.get_display_name(location)} empties {self.get_display_name(location)}.",
                    exclude=emptier,
                )

    def get_liquid(self):
        """Return the current liquid stored, or None."""
        return self.db.liquid
