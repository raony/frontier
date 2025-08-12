"""In-game time events using Evennia's custom gametime contrib.

Schedules daily sunrise and sunset messages using the custom calendar.

Based on Evennia docs (custom gametime schedule):
https://www.evennia.com/docs/latest/Howtos/Howto-Game-Time.html?highlight=time#a-game-time-with-a-custom-calendar
"""

from __future__ import annotations

from evennia.contrib.base_systems import custom_gametime
from evennia.scripts.models import ScriptDB
from evennia.objects.models import ObjectDB
from typeclasses.rooms import Room


SUNRISE_KEY = "at sunrise"
SUNSET_KEY = "at sunset"


def _broadcast_external(text: str) -> None:
    """Send message only to external rooms (tagged), including subclasses.

    We resolve rooms via tags on ObjectDB to include any room subclasses,
    then guard with a typeclass check before broadcasting.
    """
    candidates = ObjectDB.objects.filter(
        db_tags__db_key="external", db_tags__db_category="environment"
    )
    # Also include any rooms that are ExternalRoom typeclass even without tag
    rooms_qs = ObjectDB.objects.filter(db_typeclass_path__icontains="typeclasses.rooms.ExternalRoom")
    ids = set(candidates.values_list("id", flat=True))
    for r in rooms_qs:
        ids.add(r.id)
    for obj in ObjectDB.objects.filter(id__in=list(ids)):
        try:
            if obj.is_typeclass("typeclasses.rooms.Room", exact=False):
                obj.msg_contents(text)
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

    # Avoid duplicates by checking for existing scripts by key
    if not ScriptDB.objects.filter(db_key=SUNRISE_KEY).exists():
        script = custom_gametime.schedule(at_sunrise, repeat=True, hour=6, min=0, sec=0)
        script.key = SUNRISE_KEY

    if not ScriptDB.objects.filter(db_key=SUNSET_KEY).exists():
        script = custom_gametime.schedule(at_sunset, repeat=True, hour=18, min=0, sec=0)
        script.key = SUNSET_KEY
