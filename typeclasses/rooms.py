"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.contrib.base_systems import custom_gametime as gametime
import evennia

# Hex tile typeclass
from .hextile import HexTile

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    # --- Hex linkage ---------------------------------------------------------
    def set_hex_by_coords(self, q: int, r: int, s: int):
        """Link this room to a hex tile identified by cube coords.

        Stores the `HexTile.id` in an Evennia Attribute `hex_id` (category
        "environment"). Creates the `HexTile` if it does not exist.
        """
        # q + r + s must be 0 for valid cube coords; enforce lightly here
        if (q + r + s) != 0:
            raise ValueError("Hex cube coords must satisfy q + r + s == 0")

        tile, _created = HexTile.get_or_create_by_coords(q, r, s, terrain="plain")
        # Store dbref to make it easy to resolve later in-game
        self.attributes.add("hex_dbref", tile.dbref, category="environment")
        return tile

    def set_hex(self, tile: HexTile):
        """Link this room to an existing `HexTile` instance."""
        if not isinstance(tile, HexTile):
            raise TypeError("tile must be a HexTile instance")
        self.attributes.add("hex_dbref", tile.dbref, category="environment")
        return tile

    def get_hex_tile(self) -> HexTile | None:
        """Return the linked `HexTile` or None if not linked."""
        dbref = self.attributes.get("hex_dbref", category="environment", default=None)
        if not dbref:
            return None
        objs = evennia.search_object(dbref)
        return objs[0] if objs else None

    def get_hex_coords(self) -> tuple[int, int, int] | None:
        """Return (q, r, s) for the linked hex or None if not linked."""
        tile = self.get_hex_tile()
        if tile is None:
            return None
        return (int(tile.db.q or 0), int(tile.db.r or 0), int(tile.db.s or 0))

    # --- Macro attributes via hex -------------------------------------------
    def get_hex_weather(self) -> str:
        """Return current macro weather from the linked hex.

        Placeholder: Until a dedicated weather system is added on `HexTile`,
        this uses a simple mapping from terrain to a representative weather.
        """
        tile = self.get_hex_tile()
        if tile is None:
            return "clear"
        terrain = (getattr(tile.db, "terrain", "") or "").lower()
        terrain_to_weather = {
            "plain": "clear",
            "plains": "clear",
            "forest": "overcast",
            "mountain": "windy",
            "hills": "breezy",
            "swamp": "humid",
            "desert": "dry",
            "tundra": "snow",
            "coast": "breezy",
            "ocean": "stormy",
        }
        return terrain_to_weather.get(terrain, "clear")


class ExternalRoom(Room):
    """Outdoor room whose sunlight level follows game time.

    Sunlight is an integer 0..100 where 0 is night and 100 is midday.
    It ramps during dawn and dusk hours.
    """

    # Dawn/Dusk configuration (in-game hours)
    DAWN_START_HOUR: int = 5
    DAWN_END_HOUR: int = 7
    DUSK_START_HOUR: int = 18
    DUSK_END_HOUR: int = 20

    def at_object_creation(self):
        super().at_object_creation()
        # Mark this room as external for potential content logic
        self.tags.add("external", category="environment")

    # --- Sunlight helpers -------------------------------------------------
    def _current_game_time_hours(self) -> float:
        """Return current in-game time as fractional hours (0..24)."""
        # Custom gametime returns (y, m, d, h, min, sec) with absolute=True
        year, month, day, hour, minute, second = gametime.custom_gametime(absolute=True)
        return float(hour) + float(minute) / 60.0 + float(second) / 3600.0

    def compute_sunlight_level(self) -> int:
        """Compute sunlight level 0..100 from game time with dawn/dusk ramps."""
        t = self._current_game_time_hours()
        dawn_start = float(self.DAWN_START_HOUR)
        dawn_end = float(self.DAWN_END_HOUR)
        dusk_start = float(self.DUSK_START_HOUR)
        dusk_end = float(self.DUSK_END_HOUR)

        if t < dawn_start or t >= dusk_end:
            return 0
        if dawn_start <= t < dawn_end:
            # Linear ramp 0 -> 100 across dawn window
            frac = (t - dawn_start) / max(dawn_end - dawn_start, 1e-6)
            return int(round(100.0 * max(0.0, min(frac, 1.0))))
        if dusk_start <= t < dusk_end:
            # Linear ramp 100 -> 0 across dusk window
            frac = (t - dusk_start) / max(dusk_end - dusk_start, 1e-6)
            return int(round(100.0 * (1.0 - max(0.0, min(frac, 1.0)))))
        # Daytime outside ramps -> full brightness
        return 100

    def get_sunlight_level(self) -> int:
        """Return the current sunlight level 0..100, computed on demand."""
        return self.compute_sunlight_level()

    def get_light_level(self, looker=None) -> int:
        """Ambient light level for this room, including sunlight.

        Future: Sum with contained light sources (torches, lamps) and clamp 0..100.
        """
        return self.get_sunlight_level()
