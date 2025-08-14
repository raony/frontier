"""Evennia typeclass representing a hex tile for macro world attributes."""

from evennia import create_object, search_tag
from evennia.objects.objects import DefaultObject

from .objects import ObjectParent


class HexTile(ObjectParent, DefaultObject):
    """A non-movable object representing a hex tile on the world map.

    Stores cube coordinates (q, r, s) and macro attributes like terrain, weather, etc.
    Coordinates are enforced via tagging for easy lookup.
    """

    # AttributeProperty would be ideal, but we keep direct .db usage to avoid extra deps here

    @staticmethod
    def _coord_tag(q: int, r: int, s: int) -> tuple[str, str]:
        return (f"{q},{r},{s}", "hexcoord")

    @classmethod
    def get_by_coords(cls, q: int, r: int, s: int):
        tag, cat = cls._coord_tag(q, r, s)
        res = search_tag(tag, category=cat)
        # Filter to only this typeclass
        res = [obj for obj in res if obj.is_typeclass(cls, exact=False)]
        return res[0] if res else None

    @classmethod
    def get_or_create_by_coords(cls, q: int, r: int, s: int, terrain: str | None = None):
        if (q + r + s) != 0:
            raise ValueError("Hex cube coords must satisfy q + r + s == 0")
        existing = cls.get_by_coords(q, r, s)
        if existing:
            return existing, False
        key = f"Hex {q},{r},{s}"
        obj = create_object(cls, key=key, location=None, home=None)
        obj.locks.add("get:true();call:true();pick_up:false()")
        obj.db.q = int(q)
        obj.db.r = int(r)
        obj.db.s = int(s)
        if terrain is not None:
            obj.db.terrain = str(terrain)
        tag, cat = cls._coord_tag(q, r, s)
        obj.tags.add(tag, category=cat)
        return obj, True

    # Convenience accessors
    def get_coords(self) -> tuple[int, int, int]:
        return int(self.db.q or 0), int(self.db.r or 0), int(self.db.s or 0)

    def set_terrain(self, terrain: str):
        self.db.terrain = str(terrain)
