"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """Base exit connecting two rooms."""

    pass


class EasyExit(Exit):
    """Exit that requires little effort to traverse."""

    tiredness_cost = 10

    def at_post_traverse(self, traversing_object, source_location, **kwargs):
        """Increase tiredness when traversed."""
        super().at_post_traverse(traversing_object, source_location, **kwargs)
        if hasattr(traversing_object, "increase_tiredness"):
            traversing_object.increase_tiredness(self.tiredness_cost)


class HardExit(Exit):
    """Exit that requires a lot of effort to traverse."""

    tiredness_cost = 30

    def at_post_traverse(self, traversing_object, source_location, **kwargs):
        """Increase tiredness when traversed."""
        super().at_post_traverse(traversing_object, source_location, **kwargs)
        if hasattr(traversing_object, "increase_tiredness"):
            traversing_object.increase_tiredness(self.tiredness_cost)
