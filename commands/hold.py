"""Hold and release items in hands.

Holdables are separate from equippable wear slots. Items must have
`db.is_holdable=True` (e.g., via `HoldableMixin`) to be held.
"""

from .command import Command
from typeclasses.holding import NoSlotsError, NotHoldableError


class CmdHold(Command):
    """Hold a carried item in your hand.

    Usage:
      hold/<slot> <item>
    """

    key = "hold"
    locks = "cmd:tag(holder, category=holding)"

    def func(self):
        caller = self.caller
        item_key = self.lhs
        slot_key = self.switches[0] if self.switches else None

        if not item_key:
            caller.msg("Hold what?")
            return

        obj = caller.search(item_key, quiet=True)
        if not obj:
            return caller.msg(f"You don't have {item_key}.")

        if obj.location != caller:
            caller.execute_cmd(f"get {obj.get_display_name(caller)}")

        try:
            slot = caller.held_items.add(obj, slot_key)
            caller.msg(f"You hold {obj.get_display_name(caller)} in your {slot}.")
        except NoSlotsError:
            caller.msg("Your hands are full.")
        except NotHoldableError:
            caller.msg(f"You can't hold {obj.get_display_name(caller)}.")


class CmdRelease(Command):
    """Release a held item from your hand(s).

    Usage:
      release <item>
      unhold <item>
    """

    key = "release"
    aliases = ["unhold"]
    locks = "cmd:tag(holder, category=holding)"

    def func(self):
        caller = self.caller
        item_key = self.lhs

        if not item_key:
            caller.msg("Release what?")
            return

        obj = caller.search(item_key, quiet=True)
        obj_name = obj.get_display_name(caller) if obj else item_key
        if caller.held_items.remove(obj):
            caller.msg(f"You release {obj_name}.")
        else:
            caller.msg(f"You are not holding {obj_name}.")


class CmdLight(Command):
    """Light a torch or other consumable light source you carry.

    Usage:
      light <item>
      ignite <item>
    """

    key = "light"
    aliases = ["ignite"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Light what?")
            return
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        if not hasattr(obj, "turn_on"):
            caller.msg("You can't light that.")
            return
        obj.turn_on(caller=caller)


class CmdExtinguish(Command):
    """Extinguish a lit item.

    Usage:
      extinguish <item>
      douse <item>
      putout <item>
    """

    key = "extinguish"
    aliases = ["douse", "putout", "putoff"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Extinguish what?")
            return
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        if not hasattr(obj, "turn_off"):
            caller.msg("You can't extinguish that.")
            return
        obj.turn_off(caller=caller)


class CmdDarkvision(Command):
    """Toggle darkvision for builders to see in dark areas.

    Usage:
      darkvision
    """

    key = "darkvision"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        if not hasattr(caller, "light_threshold"):
            caller.msg("You don't have light perception.")
            return

        current = int(caller.light_threshold)
        if current > 0:
            # Enable darkvision by setting threshold to 0
            caller.light_threshold = 0
            caller.msg("Darkvision enabled. You can now see in complete darkness.")
        else:
            # Disable darkvision by restoring normal threshold
            caller.light_threshold = 20
            caller.msg("Darkvision disabled. You now require light to see.")
