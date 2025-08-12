"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.contrib.base_systems import custom_gametime as gametime

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

    pass


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
