"""
Equip/unequip and enhanced inventory display.
"""

from commands.command import Command


class CmdEquip(Command):
    """Equip an item using the tag-based system.

    Usage:
      equip <item>
      wear <item>
    """

    key = "equip"
    aliases = ["wear"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target_name = self.lhs

        obj = caller.quiet_search(target_name)
        if not obj:
            caller.msg(f"You don't have {target_name}.")
            return

        if obj.location != caller:
            caller.execute_cmd(f"get {obj.get_display_name(caller)}")

        caller.msg(f"You equip {obj.get_display_name()}.")
        caller.equipment.add(obj)