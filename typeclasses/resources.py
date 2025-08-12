"""Room resource objects used by internal mechanics (e.g., foraging).

Resources are in-world objects (spawnable in-game) that are hidden from
players and used to drive mechanics like foraging. Builders can create and
place them without a reload.
"""

from evennia.objects.objects import DefaultObject


class Resource(DefaultObject):
    """Generic resource object.

    Attributes:
      db.kind: str - resource kind (e.g., "foraging").
      db.abundance: int - how many times this can be harvested before depletion.
      db.quality: int - 1..3 informal quality tier influencing outcomes.
    """

    def at_object_creation(self):
        super().at_object_creation()
        # Identify as a resource and hide from normal view/get
        self.tags.add("resource", category="system")
        self.locks.add("view:false();get:false()")

        # Defaults (tweak in-game with @set)
        if self.db.kind is None:
            self.db.kind = "foraging"
        if self.db.abundance is None:
            self.db.abundance = 5
        if self.db.quality is None:
            self.db.quality = 1

        # Tag also by kind for efficient search
        if self.db.kind:
            self.tags.add(f"resource:{self.db.kind}", category="system")

    def at_after_move(self, source_location, **kwargs):
        """Keep kind tag in sync when moved or kind changed."""
        super().at_after_move(source_location, **kwargs)
        # Re-apply kind tag to be safe
        self.tags.remove(category="system", tag=f"resource:{getattr(self.db, 'kind', None)}")
        if self.db.kind:
            self.tags.add(f"resource:{self.db.kind}", category="system")

    @property
    def is_depleted(self) -> bool:
        try:
            return int(self.db.abundance or 0) <= 0
        except (TypeError, ValueError):
            return True
