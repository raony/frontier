"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia import AttributeProperty, search_object

from commands.dead_cmdset import DeadCmdSet
from commands.default_cmdsets import AliveCmdSet

from .objects import ObjectParent
from django.conf import settings
from .equipment import EQUIPMENT_SLOTS, default_equipment_map, normalize_slot


class LivingMixin:
    """Common functionality for all living entities."""

    is_pc = False

    hunger = AttributeProperty(default=0.0)
    thirst = AttributeProperty(default=0.0)
    tiredness = AttributeProperty(default=0.0)
    is_resting = AttributeProperty(default=False)
    is_dead = AttributeProperty(default=False)
    is_living = AttributeProperty(default=True)
    metabolism = AttributeProperty(default=1.0)
    # Skills stored as mapping {skill_key: level_label}
    skills = AttributeProperty(default=dict)
    # Visual perception threshold (0..100). If ambient light (sunlight) in the
    # room is below this value, the character cannot see details.
    light_threshold = AttributeProperty(default=20)

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()
        # Attribute defaults are handled by AttributeProperty

    def at_object_post_creation(self):
        """Called after initial creation and attribute setup."""
        super().at_object_post_creation()

        self.start_metabolism_script()

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.pk and getattr(self._state, "db", None):
            if self.is_living:
                self.start_metabolism_script()
            else:
                self.stop_metabolism_script()

    def at_death(self):
        """Handle death of this entity."""
        if self.location:
            self.location.msg_contents(
                "$You() collapse lifelessly.",
                from_obj=self,
            )
        self.is_dead = True
        self.is_living = False
        self.is_resting = False
        self.stop_metabolism_script()
        # Remove alive-only commands and add dead cmdset
        self.cmdset.remove(AliveCmdSet)
        self.cmdset.add(DeadCmdSet, persistent=True)

    # Hunger/thirst/tiredness management helpers
    def _hunger_level(self) -> int:
        """Return the current hunger level step."""
        hunger = self.hunger or 0
        if hunger >= 60:
            return 3
        if hunger >= 30:
            return 2
        if hunger >= 7:
            return 1
        return 0

    def _notify_hunger(self) -> None:
        """Send hunger warning messages when levels change."""
        level = self._hunger_level()
        last = getattr(self.ndb, "hunger_msg_level", None)
        if level != last:
            if level == 1:
                self.msg("You feel hungry.")
            elif level == 2:
                self.msg("You're starving.")
            elif level == 3:
                self.msg("You're gonna die.")
            self.ndb.hunger_msg_level = level

    def _thirst_level(self) -> int:
        """Return the current thirst level step."""
        thirst = self.thirst or 0
        if thirst >= 60:
            return 3
        if thirst >= 30:
            return 2
        if thirst >= 7:
            return 1
        return 0

    def _notify_thirst(self) -> None:
        """Send thirst warning messages when levels change."""
        level = self._thirst_level()
        last = getattr(self.ndb, "thirst_msg_level", None)
        if level != last:
            if level == 1:
                self.msg("You feel thirsty.")
            elif level == 2:
                self.msg("You're starving for water.")
            elif level == 3:
                self.msg("You're gonna die of thirst.")
            self.ndb.thirst_msg_level = level

    def _tiredness_level(self) -> int:
        """Return the current tiredness level step."""
        tiredness = self.tiredness or 0
        if tiredness >= 60:
            return 3
        if tiredness >= 30:
            return 2
        if tiredness >= 7:
            return 1
        return 0

    def _notify_tiredness(self) -> None:
        """Send tiredness warning messages when levels change."""
        level = self._tiredness_level()
        last = getattr(self.ndb, "tiredness_msg_level", None)
        if level != last:
            if level == 1:
                self.msg("You feel tired.")
            elif level == 2:
                self.msg("You are exhausted.")
            elif level == 3:
                self.msg("You're about to collapse.")
            self.ndb.tiredness_msg_level = level

    # Public-facing label helpers
    def get_hunger_label(self) -> str:
        """Return a user-facing hunger label without numbers."""
        level = self._hunger_level()
        return ["sated", "hungry", "starving", "starving to death"][level]

    def get_thirst_label(self) -> str:
        """Return a user-facing thirst label without numbers."""
        level = self._thirst_level()
        return ["quenched", "thirsty", "parched", "dying of thirst"][level]

    def get_tiredness_label(self) -> str:
        """Return a user-facing tiredness label without numbers."""
        level = self._tiredness_level()
        return ["rested", "tired", "exhausted", "about to collapse"][level]

    # Skills helpers
    def get_skill_level_label(self, skill_key: str) -> str:
        """Return the textual skill level for a given skill key.

        Levels are textual among {untrained, novice, journeyman, master}. Defaults to untrained.
        """
        skills_map = self.skills or {}
        level = (skills_map.get(skill_key) or "untrained").lower()
        if level not in {"untrained", "novice", "journeyman", "master"}:
            level = "untrained"
        return level

    def set_skill_level_label(self, skill_key: str, level_label: str) -> None:
        """Set the textual skill level for a given skill key."""
        if level_label not in {"untrained", "novice", "journeyman", "master"}:
            raise ValueError("Invalid skill level label")
        skills_map = self.skills or {}
        skills_map[skill_key] = level_label
        self.skills = skills_map

    # Hunger/thirst/tiredness management
    def increase_hunger(self, amount: float = 0.3) -> None:
        """Increase hunger and check for death."""
        self.hunger = (self.hunger or 0) + amount
        self._notify_hunger()
        self.update_living_status()

    def decrease_hunger(self, amount: float = 1) -> None:
        """Decrease hunger, not going below zero."""
        self.hunger = max((self.hunger or 0) - amount, 0)
        self._notify_hunger()
        self.update_living_status()

    def increase_thirst(self, amount: float = 1.4) -> None:
        """Increase thirst and check for death."""
        self.thirst = (self.thirst or 0) + amount
        self._notify_thirst()
        self.update_living_status()

    def decrease_thirst(self, amount: float = 1) -> None:
        """Decrease thirst, not going below zero."""
        self.thirst = max((self.thirst or 0) - amount, 0)
        self._notify_thirst()
        self.update_living_status()

    def increase_tiredness(self, amount: float = 0.5) -> None:
        """Increase tiredness and check for death."""
        self.tiredness = (self.tiredness or 0) + amount
        self._notify_tiredness()
        self.update_living_status()

    def decrease_tiredness(self, amount: float = 1) -> None:
        """Decrease tiredness, not going below zero."""
        self.tiredness = max((self.tiredness or 0) - amount, 0)
        self._notify_tiredness()
        self.update_living_status()

    def update_living_status(self) -> None:
        """Check if this entity should die based on vital stats."""
        if self.is_dead:
            return
        if (
            (self.hunger or 0) >= 100
            or (self.thirst or 0) >= 100
            or (self.tiredness or 0) >= 100
        ):
            self.at_death()

    # Metabolism script management
    def get_metabolism_interval(self) -> float:
        """Return real-time seconds per metabolism tick based on metabolism.

        We define one metabolism 'tick' as one in-game hour to align with
        world time. With the global time scale, one in-game hour equals
        ``REAL_SECONDS_PER_GAME_HOUR`` real seconds. The character's
        ``metabolism`` scales this frequency (higher metabolism → shorter interval).
        """
        value = self.metabolism if hasattr(self, "metabolism") else 1.0
        try:
            effective = float(value)
        except (TypeError, ValueError):
            effective = 1.0
        effective = max(effective, 0.1)
        # Base interval (real seconds) for one in-game hour, adjusted by metabolism
        time_factor = float(getattr(settings, "TIME_FACTOR", 1.0)) or 1.0
        # With custom gametime, an in-game hour is still 3600 seconds in the units
        # defined by TIME_UNITS; TIME_FACTOR governs acceleration.
        real_seconds_per_game_hour = 3600.0 / time_factor
        return real_seconds_per_game_hour / effective

    def start_metabolism_script(self) -> None:
        """Start or update the metabolism script if needed."""
        if not self.is_living:
            return
        existing = self.scripts.get("metabolism_script")
        interval = self.get_metabolism_interval()
        if existing:
            script = existing[0]
            script.interval = interval
            if not script.is_active:
                script.start()
        else:
            script = self.scripts.add(
                "typeclasses.scripts.MetabolismScript",
                key="metabolism_script",
            )
            if script:
                script.interval = interval
                script.persistent = True

    def stop_metabolism_script(self) -> None:
        """Stop the metabolism script if it exists."""
        for script in self.scripts.get("metabolism_script"):
            script.stop()
            script.delete()


class Character(LivingMixin, ObjectParent, DefaultCharacter):
    """Represents the in-game character entity.

    Three persistent Attributes are introduced on all characters:
    ``hunger``, ``thirst`` and ``tiredness``. They are integers tracking
    how hungry, thirsty or tired a character is. Newly created characters
    start at ``0`` for all values.
    """

    is_pc = True

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()
        # Initialize equipment mapping lazily to avoid Attribute creation during init sync

    def at_pre_move(self, destination, **kwargs):
        """Prevent dead characters from moving under their own power."""
        if self.is_dead:
            self.msg("You are dead and cannot move.")
            return False
        return super().at_pre_move(destination, **kwargs)

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.is_dead:
            self.cmdset.remove(AliveCmdSet)
            self.cmdset.add(DeadCmdSet, persistent=True)
        else:
            self.cmdset.remove(DeadCmdSet)
            self.cmdset.add(AliveCmdSet, persistent=True)
        self.update_living_status()

    def at_death(self):
        """Handle character-specific death effects."""
        super().at_death()
        self.cmdset.remove(AliveCmdSet)
        self.cmdset.add(DeadCmdSet, persistent=True)

    # --- Perception / Look -------------------------------------------------
    def _get_ambient_sunlight(self) -> int:
        """Return ambient light level (0..100) from current location."""
        room = self.location
        if room and hasattr(room, "get_light_level"):
            try:
                level = int(room.get_light_level(looker=self))
            except Exception:
                level = 100
            return max(0, min(level, 100))
        return 100

    def at_look(self, target, **kwargs):
        """Gate visibility based on ambient light vs character threshold."""
        ambient = self._get_ambient_sunlight()
        threshold = int(self.light_threshold or 0)
        if ambient < threshold:
            return "it is too dark to see anything"
        return super().at_look(target, **kwargs)

    def at_object_leave(self, obj, target_location, move_type="move", **kwargs):
        """Ensure equipment mapping stays consistent when items leave inventory."""
        try:
            super().at_object_leave(obj, target_location, move_type=move_type, **kwargs)  # type: ignore[misc]
        except Exception:
            # Be permissive if MRO differs
            pass
        equipped = getattr(self.db, "equipment", None) or {}
        for slot, obj_id in list(equipped.items()):
            try:
                if obj_id and int(obj_id) == int(getattr(obj, "id", -1)):
                    equipped[slot] = None
            except Exception:
                continue
        self.db.equipment = equipped
        # Also clear from holding if it was held
        try:
            obj_id_int = int(getattr(obj, "id", -1))
        except Exception:
            obj_id_int = -1
        held_list = getattr(self.db, "holding", None) or []
        if held_list and obj_id_int in held_list:
            self.db.holding = [oid for oid in held_list if int(oid) != obj_id_int]

    # --- Equipment API -----------------------------------------------------
    def _normalize_equipment_mapping(self) -> None:
        """Ensure equipment mapping stores only ints (object ids) or None."""
        mapping = getattr(self.db, "equipment", None) or {}
        changed = False
        for slot in EQUIPMENT_SLOTS:
            value = mapping.get(slot)
            if value is None:
                continue
            # Already an int id
            try:
                if isinstance(value, int):
                    continue
                # If it looks like a dbref string "#123" or "123"
                if isinstance(value, str):
                    s = value.strip().lstrip("#")
                    if s.isdigit():
                        mapping[slot] = int(s)
                        changed = True
                        continue
                # If it's an object instance with id
                obj_id = int(getattr(value, "id", 0))
                if obj_id > 0:
                    mapping[slot] = obj_id
                    changed = True
                else:
                    mapping[slot] = None
                    changed = True
            except Exception:
                mapping[slot] = None
                changed = True
        if changed:
            self.db.equipment = mapping
    def get_equipped(self):
        """Return the equipment mapping {slot: obj_id (int) or None}."""
        mapping = getattr(self.db, "equipment", None)
        if not mapping:
            # Do not create attribute in early init/sync; return a transient default
            return default_equipment_map()
        # Keep it normalized on access
        self._normalize_equipment_mapping()
        return getattr(self.db, "equipment", mapping)

    def get_equipped_in_slot(self, slot: str):
        slot_key = normalize_slot(slot)
        if not slot_key:
            return None
        obj_id = (self.get_equipped() or {}).get(slot_key)
        return self._resolve_object_id(obj_id)

    def _resolve_object_id(self, obj_id):
        """Return object instance from an object id (int/dbref) or None."""
        if not obj_id:
            return None
        try:
            obj_id_int = int(obj_id)
        except Exception:
            return None
        try:
            results = search_object(f"#{obj_id_int}")
            return results[0] if results else None
        except Exception:
            return None

    def can_equip(self, obj) -> tuple[bool, str]:
        """Check if object can be equipped and return (ok, reason_if_not)."""
        if not obj or obj.location != self:
            return False, "You must carry it to equip it."
        slot = getattr(obj, "equipable_slot", None)
        if not slot:
            return False, "You can't equip that."
        if slot not in EQUIPMENT_SLOTS:
            return False, "That doesn't fit anywhere."
        equipped_id = self.get_equipped().get(slot)
        if equipped_id and int(equipped_id) == int(getattr(obj, "id", 0)):
            return False, f"You already wear {obj.get_display_name(self)}."
        return True, ""

    def equip(self, obj) -> bool:
        """Equip an object. Returns True on success, False otherwise."""
        ok, reason = self.can_equip(obj)
        if not ok:
            self.msg(reason)
            return False
        slot = obj.equipable_slot
        equipped = self.get_equipped()
        previous_id = equipped.get(slot)
        equipped[slot] = int(obj.id)
        self.db.equipment = equipped
        if previous_id and int(previous_id) != int(obj.id):
            previous_obj = self._resolve_object_id(previous_id)
            prev_name = previous_obj.get_display_name(self) if previous_obj else "your previous item"
            self.msg(f"You replace {prev_name} with {obj.get_display_name(self)} on your {slot}.")
        else:
            self.msg(f"You equip {obj.get_display_name(self)} on your {slot}.")
        return True

    def unequip(self, slot_or_obj) -> bool:
        """Unequip by slot name or object reference. Returns True if something was unequipped."""
        equipped = self.get_equipped()
        target_slot = None
        target_obj = None
        # Accept either slot string or object
        if isinstance(slot_or_obj, str):
            target_slot = normalize_slot(slot_or_obj)
            if target_slot:
                obj_id = equipped.get(target_slot)
                target_obj = self._resolve_object_id(obj_id)
        else:
            # assume object
            for s, obj_id in equipped.items():
                try:
                    if obj_id and int(obj_id) == int(getattr(slot_or_obj, "id", 0)):
                        target_slot = s
                        target_obj = self._resolve_object_id(obj_id)
                        break
                except Exception:
                    continue
        if not target_slot or not target_obj:
            self.msg("Nothing to unequip.")
            return False
        equipped[target_slot] = None
        self.db.equipment = equipped
        self.msg(f"You remove {target_obj.get_display_name(self)} from your {target_slot}.")
        return True

    def get_equipment_display_lines(self) -> list[str]:
        """Return human-readable equipment lines for display in inventory/status."""
        lines: list[str] = []
        equipped = self.get_equipped()
        for slot in EQUIPMENT_SLOTS:
            obj_id = equipped.get(slot)
            if obj_id:
                obj = self._resolve_object_id(obj_id)
                if obj:
                    lines.append(f"{slot.capitalize():<6}: {obj.get_display_name(self)}")
                else:
                    lines.append(f"{slot.capitalize():<6}: [missing]")
            else:
                lines.append(f"{slot.capitalize():<6}: [empty]")
        return lines

    # --- Holding API ---------------------------------------------------------
    def _normalize_holding(self) -> None:
        """Ensure holding list stores only ints (object ids) present in inventory."""
        raw = getattr(self.db, "holding", None) or []
        normalized: list[int] = []
        for value in raw:
            try:
                obj_id = int(value)
            except Exception:
                try:
                    obj_id = int(getattr(value, "id", 0))
                except Exception:
                    obj_id = 0
            if obj_id:
                normalized.append(obj_id)
        # Filter out items no longer carried
        carried_ids = {int(getattr(o, "id", 0)) for o in (self.contents or [])}
        normalized = [oid for oid in normalized if oid in carried_ids]
        # Enforce capacity
        capacity = self.get_holding_capacity()
        if len(normalized) > capacity:
            normalized = normalized[:capacity]
        self.db.holding = normalized

    def get_holding_capacity(self) -> int:
        """Number of items that can be held at once."""
        return 2

    def get_holding(self) -> list[int]:
        """Return list of held object ids."""
        raw = getattr(self.db, "holding", None)
        if raw is None:
            return []
        self._normalize_holding()
        return list(getattr(self.db, "holding", []))

    def _resolve_any(self, obj_or_id):
        if not obj_or_id:
            return None
        if isinstance(obj_or_id, int):
            return self._resolve_object_id(obj_or_id)
        return obj_or_id

    def is_holdable(self, obj) -> bool:
        try:
            return bool(getattr(getattr(obj, "db", object()), "is_holdable", False))
        except Exception:
            return False

    def can_hold(self, obj) -> tuple[bool, str]:
        if not obj or obj.location != self:
            return False, "You must carry it to hold it."
        if not self.is_holdable(obj):
            return False, "You can't hold that."
        held = self.get_holding()
        if any(int(oid) == int(getattr(obj, "id", 0)) for oid in held):
            return False, f"You already hold {obj.get_display_name(self)}."
        if len(held) >= self.get_holding_capacity():
            return False, "Your hands are full."
        return True, ""

    def hold(self, obj) -> bool:
        ok, reason = self.can_hold(obj)
        if not ok:
            self.msg(reason)
            return False
        held = self.get_holding()
        held.append(int(obj.id))
        self.db.holding = held
        self.msg(f"You hold {obj.get_display_name(self)} in your hand.")
        return True

    def release(self, obj_or_all) -> bool:
        """Release a held item by object or use string 'all' to free hands."""
        held = self.get_holding()
        if not held:
            self.msg("Your hands are empty.")
            return False
        if isinstance(obj_or_all, str) and obj_or_all.strip().lower() == "all":
            self.db.holding = []
            self.msg("You relax your grip and free your hands.")
            return True
        obj = self._resolve_any(obj_or_all)
        if not obj:
            self.msg("You don't hold that.")
            return False
        try:
            obj_id = int(getattr(obj, "id", 0))
        except Exception:
            obj_id = 0
        if not obj_id or obj_id not in held:
            self.msg("You don't hold that.")
            return False
        self.db.holding = [oid for oid in held if int(oid) != obj_id]
        self.msg(f"You release {obj.get_display_name(self)}.")
        return True

    def get_holding_display_line(self) -> str:
        held = self.get_holding()
        if not held:
            return "Held: [empty]"
        names: list[str] = []
        for oid in held:
            obj = self._resolve_object_id(oid)
            if obj:
                names.append(obj.get_display_name(self))
        return "Held: " + (", ".join(names) if names else "[missing]")
