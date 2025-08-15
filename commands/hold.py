"""Hold and release items in hands.

Holdables are separate from equippable wear slots. Items must have
`db.is_holdable=True` (e.g., via `HoldableMixin`) to be held.
"""

from .command import Command
from typeclasses.holding import AlreadyHoldingError, NoSlotsError, NotHoldableError, InvalidSlotError


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

        obj = caller.quiet_search(item_key)
        if not obj:
            return caller.msg(f"You don't have {item_key}.")

        if obj.location != caller:
            caller.execute_cmd(f"get {obj.get_display_name(caller)}")

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

        try:
            name = obj.get_display_name(caller)
            if caller.held_items.add(obj, slots=slot_keys):
                slot_display = caller.get_display_holding(obj)
                caller.msg(f"You hold {name} in your {slot_display}.")
            else:
                caller.msg(f"You are already holding {name}.")
        except InvalidSlotError:
            caller.msg(f"What is {slot_keys[0]}?")
        except (NoSlotsError, AlreadyHoldingError):
            caller.msg("Your hands are full.")
        except NotHoldableError:
            caller.msg(f"You can't hold {obj.get_display_name(caller)}.")