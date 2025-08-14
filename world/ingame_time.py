"""In-game time events using Evennia's custom gametime contrib.

Schedules daily sunrise and sunset messages using the custom calendar.

Based on Evennia docs (custom gametime schedule):
https://www.evennia.com/docs/latest/Howtos/Howto-Game-Time.html?highlight=time#a-game-time-with-a-custom-calendar
"""

from __future__ import annotations

from evennia.contrib.base_systems import custom_gametime
from evennia.scripts.models import ScriptDB
from evennia.utils.search import search_typeclass


SUNRISE_KEY = "at sunrise"
SUNSET_KEY = "at sunset"


def _broadcast_external(text: str) -> None:
    """Send message to all rooms of type `typeclasses.rooms.ExternalRoom`.

    Uses Evennia's object search by typeclass, including subclasses when exact=False.
    """
    rooms = search_typeclass("typeclasses.rooms.ExternalRoom", include_children=True)

    for room in rooms:
        try:
            room.msg_contents(text)
        except Exception:
            continue


def at_sunrise():
    """Announce sunrise to external rooms only."""
    _broadcast_external("The sun rises from the eastern horizon.")


def at_sunset():
    """Announce sunset to external rooms only."""
    _broadcast_external("The sun sets beyond the western horizon.")


def start_time_events():
    """Ensure daily sunrise and sunset events are scheduled once.

    Uses custom_gametime.schedule with repeat=True so events fire every in-game day
    at the specified hour/min/sec according to the custom calendar/time factor.
    """

    def _unschedule(key: str) -> None:
        for script in ScriptDB.objects.filter(db_key=key):
            try:
                script.stop()
            except Exception:
                pass
            try:
                script.delete()
            except Exception:
                pass

    # Drop any existing sunrise/sunset schedules to avoid duplicates and stale timers
    _unschedule(SUNRISE_KEY)
    _unschedule(SUNSET_KEY)

    # Schedule fresh daily events
    script = custom_gametime.schedule(at_sunrise, repeat=True, hour=6, min=0, sec=0)
    script.key = SUNRISE_KEY

    script = custom_gametime.schedule(at_sunset, repeat=True, hour=18, min=0, sec=0)
    script.key = SUNSET_KEY
