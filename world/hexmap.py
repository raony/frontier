"""Hexagonal map representation using cube coordinates.

This module defines simple data structures for representing a hexagonal
map that is completely separate from Evennia's database models and
Typeclasses.
"""

from dataclasses import dataclass
from typing import Dict, Optional


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
    """Container for hexagonal tiles indexed by cube coordinates."""

    def __init__(self) -> None:
        self._tiles: Dict[CubeCoord, Optional[object]] = {}

    def add_tile(self, coord: CubeCoord, data: Optional[object] = None) -> None:
        self._tiles[coord] = data

    def get_tile(self, coord: CubeCoord) -> Optional[object]:
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
