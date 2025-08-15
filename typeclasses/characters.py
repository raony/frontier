"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia import AttributeProperty, search_object, TagProperty

from .objects import ObjectParent
from django.conf import settings
from .equipment import EQUIPMENT_SLOTS, default_equipment_map, normalize_slot
from .living import LivingMixin
from .holding import HolderMixin


class Character(LivingMixin, HolderMixin, ObjectParent, DefaultCharacter):
    """Represents the in-game character entity.

    Three persistent Attributes are introduced on all characters:
    ``hunger``, ``thirst`` and ``tiredness``. They are integers tracking
    how hungry, thirsty or tired a character is. Newly created characters
    start at ``0`` for all values.
    """

    is_pc = True

    def get_tag_objs(self, *args, **kwargs):
        return self.tags.get(*args, **kwargs, return_tagobj=True)

    def at_object_creation(self):
        """Called once, when the object is first created."""
        super().at_object_creation()
        # Initialize equipment mapping lazily to avoid Attribute creation during init sync

    def at_pre_move(self, destination, **kwargs):
        """Prevent dead characters from moving under their own power."""
        if self.is_dead():
            self.msg("You are dead and cannot move.")
            return False
        return super().at_pre_move(destination, **kwargs)

    def at_init(self):
        """Called whenever the typeclass is cached from memory."""
        super().at_init()
        if self.is_dead():
            from commands.default_cmdsets import AliveCmdSet
            from commands.dead_cmdset import DeadCmdSet
            self.cmdset.remove(AliveCmdSet)
            self.cmdset.add(DeadCmdSet, persistent=True)
        else:
            from commands.default_cmdsets import AliveCmdSet
            from commands.dead_cmdset import DeadCmdSet
            self.cmdset.remove(DeadCmdSet)
            self.cmdset.add(AliveCmdSet, persistent=True)
        self.update_living_status()

    def at_death(self):
        """Handle character-specific death effects."""
        super().at_death()
        from commands.default_cmdsets import AliveCmdSet
        from commands.dead_cmdset import DeadCmdSet
        self.cmdset.remove(AliveCmdSet)
        self.cmdset.add(DeadCmdSet, persistent=True)

    # --- Perception / Look -------------------------------------------------
    def at_look(self, target, **kwargs):
        """Gate visibility based on ambient light vs character threshold."""
        # Check if we can see details in current light
        if self.location.get_light_level(looker=self) < self.light_threshold:
            return "It's too dark to see anything."
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

    # --- Equipment API --------------------------------------------------------

    def get_equipment_map(self) -> dict:
        """Return the current equipment mapping."""
        # Lazy initialization to avoid Attribute creation during init sync
        if not hasattr(self, "_equipment_map"):
            self._equipment_map = getattr(self.db, "equipment", None)
            if self._equipment_map is None:
                self._equipment_map = default_equipment_map()
                self.db.equipment = self._equipment_map
        return self._equipment_map

    def set_equipment(self, slot: str, item_id: int | None) -> None:
        """Set equipment in a slot."""
        equipment = self.get_equipment_map()
        slot = normalize_slot(slot)
        if slot:
            equipment[slot] = item_id
            self.db.equipment = equipment

    def get_equipment(self, slot: str) -> int | None:
        """Get equipment in a slot."""
        equipment = self.get_equipment_map()
        slot = normalize_slot(slot)
        return equipment.get(slot) if slot else None

    def get_equipment_display_lines(self) -> list[str]:
        """Return formatted equipment display lines."""
        equipment = self.get_equipment_map()
        lines = []
        for slot in EQUIPMENT_SLOTS:
            item_id = equipment.get(slot)
            if item_id:
                item = self._resolve_object_id(item_id)
                if item:
                    lines.append(f"  {slot.title()}: {item.get_display_name(self)}")
                else:
                    # Clean up invalid equipment reference
                    self.set_equipment(slot, None)
            else:
                lines.append(f"  {slot.title()}: <empty>")
        return lines

    def _resolve_object_id(self, obj_id: int):
        """Resolve an object ID to an actual object."""
        try:
            return search_object(f"#{obj_id}")[0] if search_object(f"#{obj_id}") else None
        except Exception:
            return None

    def get_equipped_in_slot(self, slot: str):
        """Get the object equipped in a specific slot."""
        item_id = self.get_equipment(slot)
        if item_id:
            return self._resolve_object_id(item_id)
        return None

    def equip(self, item) -> bool:
        """Equip an item to its default slot."""
        if not hasattr(item, "equipment_slot"):
            self.msg(f"{item.get_display_name(self)} cannot be equipped.")
            return False
        slot = item.equipment_slot
        self.set_equipment(slot, item.id)
        self.msg(f"You equip {item.get_display_name(self)} to your {slot}.")
        return True

    def unequip(self, slot_or_item) -> bool:
        """Unequip an item by slot name or item object."""
        if isinstance(slot_or_item, str):
            # Unequip by slot name
            slot = normalize_slot(slot_or_item)
            if not slot:
                self.msg(f"Unknown equipment slot: {slot_or_item}")
                return False
            item_id = self.get_equipment(slot)
            if not item_id:
                self.msg(f"You have nothing equipped in your {slot}.")
                return False
            self.set_equipment(slot, None)
            self.msg(f"You unequip your {slot}.")
            return True
        else:
            # Unequip by item object
            item = slot_or_item
            if not hasattr(item, "equipment_slot"):
                self.msg(f"{item.get_display_name(self)} is not equipped.")
                return False
            slot = item.equipment_slot
            current_item_id = self.get_equipment(slot)
            if current_item_id != item.id:
                self.msg(f"{item.get_display_name(self)} is not equipped.")
                return False
            self.set_equipment(slot, None)
            self.msg(f"You unequip {item.get_display_name(self)}.")
            return True
