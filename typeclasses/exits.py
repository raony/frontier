"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit
from evennia import AttributeProperty

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """Base exit connecting two rooms with effort cost on traverse."""

    # Persistent Character Attribute-style property so it can be changed with @set
    tiredness_cost = AttributeProperty(default=0)

    def at_post_traverse(self, traversing_object, source_location, **kwargs):
        """Increase tiredness when traversed based on `tiredness_cost`."""
        super().at_post_traverse(traversing_object, source_location, **kwargs)
        cost = self.tiredness_cost or 0
        if hasattr(traversing_object, "increase_tiredness") and cost:
            traversing_object.increase_tiredness(cost)


class EasyExit(Exit):
    """Exit that requires little effort to traverse."""

    def at_object_creation(self):
        super().at_object_creation()
        self.tiredness_cost = 10


class HardExit(Exit):
    """Exit that requires a lot of effort to traverse."""

    def at_object_creation(self):
        super().at_object_creation()
        self.tiredness_cost = 30
