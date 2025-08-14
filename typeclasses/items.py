"""
Concrete equippable item base classes per slot.

Use these typeclasses to create items in-game directly, e.g.:
  @create "Leather Cap":typeclasses.items.HeadItem
Then edit its desc/aliases etc as usual.
"""

from .objects import Object, LightSourceMixin
from .equipment import (
    EquippableHead,
    EquippableBody,
    EquippableLegs,
    EquippableWaist,
    EquippableHands,
    EquippableFeet,
)


class HeadItem(EquippableHead, Object):
    """Base typeclass for items that equip to the head slot."""


class BodyItem(EquippableBody, Object):
    """Base typeclass for items that equip to the body slot."""


class LegsItem(EquippableLegs, Object):
    """Base typeclass for items that equip to the legs slot."""


class WaistItem(EquippableWaist, Object):
    """Base typeclass for items that equip to the waist slot."""


class HandsItem(EquippableHands, Object):
    """Base typeclass for items that equip to the hands slot."""


class FeetItem(EquippableFeet, Object):
    """Base typeclass for items that equip to the feet slot."""


# --- Holdable items -----------------------------------------------------------

class HoldableMixin:
    """Mixin for items that can be held in hands (not worn).

    On creation, sets a persistent attribute `db.is_holdable = True` so builders
    can mark holdables and commands can validate items for holding.
    """

    def at_object_creation(self):
        try:
            super().at_object_creation()  # type: ignore[misc]
        except Exception:
            pass
        self.db.is_holdable = True


class HoldableItem(HoldableMixin, Object):
    """Base typeclass for simple items intended to be held in hand."""


# --- Consumable toggle mixin --------------------------------------------------

class ConsumableToggleMixin:
    """Mixin for items that deplete while ON.

    Persistent attributes set:
      - db.is_consumable = True
      - db.is_on = False
      - db.fuel_max (float)
      - db.fuel (float)
      - db.consume_rate (float per tick)
      - db.consume_interval (seconds per tick)
    The item should be attached to `ItemConsumptionScript` while ON.
    """

    fuel_max_default: float = 60.0
    consume_rate_default: float = 1.0
    consume_interval_default: int = 5

    def at_object_creation(self):
        try:
            super().at_object_creation()  # type: ignore[misc]
        except Exception:
            pass
        self.db.is_consumable = True
        self.db.is_on = False
        self.db.fuel_max = float(getattr(self, "fuel_max_default", 60.0))
        self.db.fuel = float(self.db.fuel_max)
        self.db.consume_rate = float(getattr(self, "consume_rate_default", 1.0))
        self.db.consume_interval = int(getattr(self, "consume_interval_default", 5))

    # --- Script control
    def get_consume_interval(self) -> int:
        try:
            return int(getattr(getattr(self, "db", object()), "consume_interval", 5) or 5)
        except Exception:
            return 5

    def _start_consumption(self) -> None:
        existing = self.scripts.get("consumption_script")
        if existing:
            script = existing[0]
            if not script.is_active:
                script.start()
            return
        script = self.scripts.add(
            "typeclasses.scripts.ItemConsumptionScript",
            key="consumption_script",
        )
        if script:
            script.interval = self.get_consume_interval()
            script.persistent = True

    def _stop_consumption(self) -> None:
        for script in self.scripts.get("consumption_script"):
            script.stop()
            script.delete()

    # --- Toggle API
    def can_turn_on(self) -> tuple[bool, str]:
        fuel = float(getattr(getattr(self, "db", object()), "fuel", 0) or 0)
        if fuel <= 0:
            return False, "It's spent."
        if getattr(getattr(self, "db", object()), "is_on", False):
            return False, "It's already lit."
        return True, ""

    def turn_on(self, caller=None) -> bool:
        ok, reason = self.can_turn_on()
        if not ok:
            if caller:
                caller.msg(reason)
            return False
        self.db.is_on = True
        self._start_consumption()
        if caller:
            caller.msg(f"You light {self.get_display_name(caller)}.")
        return True

    def turn_off(self, caller=None) -> bool:
        if not getattr(self.db, "is_on", False):
            if caller:
                caller.msg("It's already extinguished.")
            return False
        self.db.is_on = False
        self._stop_consumption()
        if caller:
            caller.msg(f"You extinguish {self.get_display_name(caller)}.")
        return True

    def _consume_tick(self) -> None:
        # Decrease fuel; if spent, turn off
        try:
            rate = float(getattr(self.db, "consume_rate", 1.0) or 1.0)
        except Exception:
            rate = 1.0
        fuel = float(getattr(self.db, "fuel", 0.0) or 0.0)
        fuel = max(0.0, fuel - max(0.0, rate))
        self.db.fuel = fuel
        if fuel <= 0:
            # Out of fuel
            self.db.is_on = False
            self._stop_consumption()
            # Optionally adjust light or notify location
            try:
                if self.location:
                    self.location.msg_contents(f"{self.get_display_name(self.location)} sputters out.")
            except Exception:
                pass


class Torch(ConsumableToggleMixin, HoldableMixin, LightSourceMixin, Object):
    """A simple handheld torch that emits light.

    This torch provides enough light to see in dark places when present in
    a room or when held/carried by someone in the room.
    """

    light_level_default = 40

    def get_light_level(self, looker=None) -> int:
        # Emit light only while lit
        try:
            is_on = bool(getattr(getattr(self, "db", object()), "is_on", False))
        except Exception:
            is_on = False
        if not is_on:
            return 0
        return super().get_light_level(looker=looker)
