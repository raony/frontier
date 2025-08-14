"""Hexagonal map representation using cube coordinates.

This module provides helpers around cube coordinates and persists hex tiles
as Evennia objects via the `typeclasses.hextile.HexTile` typeclass.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Iterable

from django.db import transaction
from typeclasses.hextile import HexTile


@dataclass(frozen=True)
class CubeCoord:
    """Cube coordinate in a hex grid."""

    q: int
    r: int
    s: int

    def __post_init__(self):
        if (self.q + self.r + self.s) != 0:
            raise ValueError("q + r + s must equal 0")


class HexMap:
    """Container for hexagonal tiles indexed by cube coordinates.

    The optional `data` stored per tile is the terrain string when using
    DB persistence via `load_all`/`save_all`.
    """

    def __init__(self) -> None:
        self._tiles: Dict[CubeCoord, Optional[str]] = {}

    def add_tile(self, coord: CubeCoord, data: Optional[str] = None) -> None:
        self._tiles[coord] = data

    def get_tile(self, coord: CubeCoord) -> Optional[str]:
        return self._tiles.get(coord)

    def neighbors(self, coord: CubeCoord):
        """Yield neighbor coordinates around `coord`."""
        directions = [
            CubeCoord(1, -1, 0),
            CubeCoord(1, 0, -1),
            CubeCoord(0, 1, -1),
            CubeCoord(-1, 1, 0),
            CubeCoord(-1, 0, 1),
            CubeCoord(0, -1, 1),
        ]
        for d in directions:
            yield CubeCoord(coord.q + d.q, coord.r + d.r, coord.s + d.s)

    # --- Persistence helpers ---
    @classmethod
    def load_all(cls) -> "HexMap":
        """Load entire map from Evennia objects into a HexMap instance."""
        hm = cls()
        # Use tag category 'hexcoord' to find all hex tiles
        from evennia import search_tag

        tiles = [obj for obj in search_tag(category="hexcoord") if obj.is_typeclass(HexTile, exact=False)]
        for obj in tiles:
            q, r, s = int(obj.db.q or 0), int(obj.db.r or 0), int(obj.db.s or 0)
            hm.add_tile(CubeCoord(q, r, s), getattr(obj.db, "terrain", None))
        return hm

    @transaction.atomic
    def save_all(self, overwrite: bool = True) -> None:
        """Persist the current map to Evennia objects (typeclass HexTile).

        - If `overwrite` is True, hex objects not present in the in-memory map are deleted.
        - Otherwise, only upserts are performed.
        """
        from evennia import search_tag

        coords_seen: set[tuple[int, int, int]] = set()
        for coord, terrain in self._tiles.items():
            coords_seen.add((coord.q, coord.r, coord.s))
            obj, _ = HexTile.get_or_create_by_coords(coord.q, coord.r, coord.s, terrain=terrain or "plain")
            if terrain is not None:
                obj.db.terrain = terrain
        if overwrite:
            # Delete hex objects not in map
            tiles = [obj for obj in search_tag(category="hexcoord") if obj.is_typeclass(HexTile, exact=False)]
            for obj in tiles:
                tup = (int(obj.db.q or 0), int(obj.db.r or 0), int(obj.db.s or 0))
                if tup not in coords_seen:
                    obj.delete()
