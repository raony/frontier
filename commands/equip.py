"""
Equip/unequip and enhanced inventory display.
"""

from evennia import default_cmds
from .command import Command


class CmdEquip(Command):
    """Equip an item you are carrying.

    Usage:
      equip <item>
      wear <item>
    """

    key = "equip"
    aliases = ["wear"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Equip what?")
            return
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        caller.equip(obj)


class CmdUnequip(Command):
    """Unequip an item by slot or by name.

    Usage:
      unequip <slot>
      remove <item>
    """

    key = "unequip"
    aliases = ["remove"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Unequip what? Specify a slot or item name.")
            return
        # Try by slot name without triggering double messages
        slot_obj = None
        if hasattr(caller, "get_equipped_in_slot"):
            slot_obj = caller.get_equipped_in_slot(self.args)
        if slot_obj:
            caller.unequip(self.args)
            return
        # Try by object name from inventory
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        caller.unequip(obj)
