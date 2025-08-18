from evennia import AttributeProperty


class WeightMixin:
    """Mixin for objects that have weight.

    Sets a default persistent `db.weight` on creation. Objects can override
    `weight_default` to change the default weight in grams. Use together with
    `Object` or other typeclasses.
    """

    weight = AttributeProperty(default=100)

    def at_object_creation(self):
        """Set the weight based on weight_default if defined."""
        super().at_object_creation()
        if hasattr(self, 'weight_default'):
            self.weight = self.weight_default

    @property
    def total_weight(self) -> int:
        """Return the total weight of this object and its contents in grams."""
        return self.weight + sum(obj.total_weight for obj in self.contents)

    def set_weight(self, weight: int) -> None:
        """Set the weight of this object in grams."""
        try:
            weight = int(weight)
            if weight < 0:
                raise ValueError("Weight cannot be negative.")
            self.weight = weight
        except ValueError:
            raise ValueError("Weight must be an integer.")

    def get_display_footer(self, looker, **kwargs):
        """Return the display footer with weight information."""
        footer = super().get_display_footer(looker, **kwargs)
        if kwargs.get("examine", False):
            return "\n".join(filter(None, [footer, f"Weight: {self.total_weight}g"]))
        else:
            return footer
