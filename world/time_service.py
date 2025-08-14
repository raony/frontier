"""Game-time computation service.

This module centralizes the math for computing the game epoch given a target
in-game time, the real-world time, and the configured time factor / calendar.

It is designed to be testable in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, Tuple


Seconds = int


@dataclass
class GameTimeService:
    """Pure service for epoch/time calculations.

    - settings: object exposing TIME_FACTOR and TIME_UNITS (optional)
    - now_provider: callable returning current real-time seconds (defaults to time.time)
    """

    settings: object
    now_provider: Callable[[], float]

    # Optional provider of server real runtime seconds; if not given, we will
    # lazily import evennia.utils.gametime.runtime when needed.
    runtime_provider: Callable[[], float] | None = None

    # -------- Helpers --------
    def get_time_factor(self) -> float:
        try:
            tf = float(getattr(self.settings, "TIME_FACTOR", 1.0))
            return tf or 1.0
        except Exception:
            return 1.0

    def get_time_units(self) -> Dict[str, int]:
        units = getattr(self.settings, "TIME_UNITS", None)
        if isinstance(units, dict) and units:
            return units
        # Default to Gregorian-like with 30-day months per custom calendar examples
        return {
            "sec": 1,
            "min": 60,
            "hour": 3600,
            "day": 86400,
            "month": 2592000,  # 30 days
            "year": 31104000,  # 360 days
        }

    # -------- Conversions --------
    def to_custom_seconds(self, y: int, mon: int, d: int, h: int, mi: int, s: int) -> Seconds:
        units = self.get_time_units()
        total = int(s)
        total += int(mi) * units["min"]
        total += int(h) * units["hour"]
        total += max(int(d) - 1, 0) * units["day"]
        total += max(int(mon) - 1, 0) * units["month"]
        total += int(y) * units["year"]
        return int(total)

    # -------- Epoch computation strategies --------
    def compute_epoch_from_desired_gregorian(self, desired_dt: datetime) -> Seconds:
        """Compute epoch so that current in-game time equals desired_dt.

        Uses real-time anchoring: game_now = epoch + real_elapsed * TIME_FACTOR.
        """
        tf = self.get_time_factor()
        real_now = float(self.now_provider())
        desired_unix = int(desired_dt.timestamp())
        epoch = int(desired_unix - real_now * tf)
        return epoch

    def compute_epoch_from_desired_using_runtime(self, desired_dt: datetime) -> Seconds:
        """Compute epoch using server runtime anchoring.

        Evennia's @time display shows 'Total time passed' ~= total runtime * TIME_FACTOR.
        The current in-game datetime is effectively

            game_now = epoch + runtime_seconds * TIME_FACTOR

        So to make game_now == desired_dt, pick

            epoch = desired_unix - runtime_seconds * TIME_FACTOR.
        """
        tf = self.get_time_factor()
        if self.runtime_provider:
            runtime_seconds = float(self.runtime_provider())
        else:
            try:
                from evennia.utils import gametime as std_gametime  # type: ignore

                runtime_seconds = float(std_gametime.runtime())
            except Exception:
                # Fallback to now_provider-based estimate (less accurate)
                runtime_seconds = 0.0
        desired_unix = int(desired_dt.timestamp())
        epoch = int(desired_unix - runtime_seconds * tf)
        return epoch

    def compute_epoch_shift_same_day_time(self, current_custom: Tuple[int, int, int, int, int, int],
                                          desired_time: Tuple[int, int, int]) -> Seconds:
        """Compute epoch shift to change only time within the same custom day.

        Returns the delta in GAME seconds to add to TIME_GAME_EPOCH directly.
        Since game_now = epoch + runtime * TIME_FACTOR, adjusting epoch by N
        moves the game clock by exactly N game-seconds (no division by factor).
        """
        cy, cmon, cday, ch, cmi, cs = current_custom
        th, tmi, ts = desired_time
        current_seconds = self.to_custom_seconds(cy, cmon, cday, ch, cmi, cs)
        desired_seconds = self.to_custom_seconds(cy, cmon, cday, th, tmi, ts)
        delta_game = desired_seconds - current_seconds
        return int(delta_game)
