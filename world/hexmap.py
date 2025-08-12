"""Hexagonal map representation using cube coordinates.

This module defines simple data structures for representing a hexagonal
map that is completely separate from Evennia's database models and
Typeclasses.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Iterable

from django.db import transaction

# DB model for persistence
from .models import HexTile


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
        """Load entire map from the database into a HexMap instance."""
        hm = cls()
        for tile in HexTile.objects.all():
            hm.add_tile(CubeCoord(tile.q, tile.r, tile.s), tile.terrain)
        return hm

    @transaction.atomic
    def save_all(self, overwrite: bool = True) -> None:
        """Persist the current map to the database.

        - If `overwrite` is True, existing rows for present coords are updated and
          any DB rows not present in the in-memory map are deleted.
        - If False, only upserts for present coords are performed and extras remain.
        """
        coords_seen: set[tuple[int, int, int]] = set()
        # Upsert tiles
        for coord, terrain in self._tiles.items():
            coords_seen.add((coord.q, coord.r, coord.s))
            HexTile.objects.update_or_create(
                q=coord.q,
                r=coord.r,
                s=coord.s,
                defaults={"terrain": terrain or "plain"},
            )
        if overwrite:
            # Delete tiles not represented in this HexMap
            qs = HexTile.objects.all()
            to_delete_ids: Iterable[int] = (
                qs.exclude(
                    q__in=[q for q, _, _ in coords_seen],
                )
                .values_list("id", flat=True)
            )
            # Further filter by matching full tuple to avoid partial collisions
            delete_ids: list[int] = []
            for tile in qs:
                tup = (tile.q, tile.r, tile.s)
                if tup not in coords_seen:
                    delete_ids.append(tile.id)
            if delete_ids:
                HexTile.objects.filter(id__in=delete_ids).delete()
