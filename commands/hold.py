"""Hold and release items in hands.

Holdables are separate from equippable wear slots. Items must have
`db.is_holdable=True` (e.g., via `HoldableMixin`) to be held.
"""

from .command import Command
from evennia.help.models import Tag


class CmdHold(Command):
    """Hold a carried item in your hand.

    Usage:
      hold/<slot> <item>
      hold/both <item>
    """

    key = "hold"
    locks = "cmd:tag(holder, category=holding)"

    def func(self):
        caller = self.caller
        item_key = self.lhs

        if not item_key:
            caller.msg("Hold what?")
            return

        switch = self.switches[0] if self.switches else None
        if not switch:
            slot_keys = []
        else:
            slot_keys = ['main', 'off'] if switch == 'both' else [switch]

        obj = caller.search_item(item_key)
        if not obj:
            return caller.msg(f"You can't find {item_key}.")

        if not caller.held_items.is_holdable(obj):
            return caller.msg(f"You can't hold {obj.get_display_name(caller)}.")

        if not slot_keys:
            current_slots = caller.held_items.get_slots_for(obj)
            if not current_slots:
                next_slot = caller.held_items.next_available_slot
                if next_slot:
                    slot_keys.append(next_slot)
                else:
                    return caller.msg("You have no free hands.")
            else:
                slot_keys = [current_slots[0]]

        if caller.held_items.is_too_heavy(obj, slot_keys):
            return caller.msg(f"{obj.get_display_name(caller)} is too heavy for you to hold.")

        if caller.held_items.is_already_holding(obj, slot_keys):
            return caller.msg(f"You are already holding {obj.get_display_name(caller)}.")

        if not caller.held_items.is_slots_available(obj, slot_keys):
            return caller.msg(f"You don't have enough free hands.")

        if obj.location != caller:
            obj.move_to(caller, quiet=True)

        if caller.held_items.can_hold(obj, slot_keys):
            if len(slot_keys) == 1:
                slot_display = Tag.objects.get(db_key=slot_keys[0], db_category="holding_slot").db_data
            else:
                slot_display = "both hands"
            caller.location.msg_contents(
                f"$You() $conj(hold) $you(obj) with {slot_display}",
                from_obj=caller,
                mapping={"obj": obj}
            )
            caller.held_items.add(obj, slots=slot_keys)
        else:
            caller.msg(f"You can't hold {obj.get_display_name(caller)}.")