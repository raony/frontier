from commands.command import Command

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
        elif switch == 'both':
            slot_keys = ['main hand', 'off hand']
        else:
            available_slots = caller.held_items.slots
            slot_keys = [slot for slot in available_slots if slot.lower().startswith(switch.lower())]

            if not slot_keys:
                return caller.msg(f"No holding slot found starting with '{switch}'.")

        obj = caller.search_item(item_key)
        if not obj:
            return caller.msg(f"You can't find {item_key}.")

        if not caller.held_items.is_holdable(obj):
            return caller.msg(f"You can't hold {self.get_display_name(obj)}.")

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
            return caller.msg(f"{self.get_display_name(obj)} is too heavy for you to hold.")

        if caller.held_items.is_already_holding(obj, slot_keys):
            return caller.msg(f"You are already holding {self.get_display_name(obj)}.")

        if not caller.held_items.is_slots_available(obj, slot_keys):
            return caller.msg(f"You don't have enough free hands.")

        if obj.location != caller:
            obj.move_to(caller, quiet=True)

        if caller.held_items.can_hold(obj, slot_keys):
            if len(slot_keys) == 1:
                slot_display = slot_keys[0]
            else:
                slot_display = "both hands"

            self.send_room_message(
                f"$You() $conj(hold) $obj(item) with {slot_display}",
                mapping={"item": obj}
            )
            caller.held_items.add(obj, slots=slot_keys)
        else:
            caller.msg(f"You can't hold {self.get_display_name(obj)}.")