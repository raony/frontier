"""Container mixin for objects that can hold other objects."""

from evennia import AttributeProperty
from typeclasses.objects import Object

def is_container(obj) -> bool:
    """Return True if the object is a container."""
    return obj.tags.has('container', category='container')

class ContainerMixin:
    """Mixin for objects that can contain other objects.
    """

    container_capacity = AttributeProperty(default=10)
    container_weight_limit = AttributeProperty(default=5000)
    container_locked = AttributeProperty(default=False)

    def at_object_creation(self):
        """Initialize container properties."""
        super().at_object_creation()  # type: ignore[misc]
        self.tags.add("container", category="container")

    def is_locked(self) -> bool:
        """Return True if the container is locked."""
        return self.container_locked

    def is_full(self) -> bool:
        """Return True if the container is full."""
        return len(self.contents) + 1 > self.container_capacity

    def is_too_heavy(self, added_item) -> bool:
        """Return True if the container is too heavy."""
        return self.weight.total + added_item.weight.total > self.container_weight_limit

    def can_hold_item(self, item) -> bool:
        """Check if this container can hold the given item."""
        if self.is_locked() or self.is_full() or self.is_too_heavy(item):
            return False

        return True

    def at_pre_object_receive(self, obj, source_location, **kwargs):
        """Called before an object is moved into this container."""

        if not self.can_hold_item(obj):
            return False

        return super().at_pre_object_receive(obj, source_location, **kwargs)


class Container(ContainerMixin, Object):
    """Base container class that can be used directly or inherited from."""

    container_capacity_default = 10
    container_weight_limit_default = 5000  # 5kg default weight limit
    weight_default = 200  # Container weight in grams

    def at_object_creation(self):
        """Initialize the container."""
        super().at_object_creation()
        self.db.container_description = "A simple container"
