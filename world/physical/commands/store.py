"""Store items in containers.

This command allows characters to store items in containers using the
ContainerMixin functionality.
"""

from commands.command import Command
from world.physical.container import is_container


class CmdStore(Command):
    """Store an item in a container.

    Usage:
      store/<container> <item>
      store <item> (auto-finds suitable container)
    """

    key = "store"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        item_key = self.lhs

        if not item_key:
            return caller.msg("Store what?")

        item = caller.search_item(item_key)
        if not item:
            return caller.msg(f"You don't have {item_key}.")

        if not self.switches:
            container = self.find_suitable_container(caller, item)
            if not container:
                return caller.msg(f"You don't have any suitable containers to store {self.get_display_name(item)} in.")
        else:
            container_key = self.switches[0]

            container = caller.search_item(container_key)
            if not container:
                return caller.msg(f"You don't see {container_key}.")

            if container == item:
                return caller.msg(f"You can't store {self.get_display_name(item)} in itself.")

            if not is_container(container):
                return caller.msg(f"{self.get_display_name(container)} is not a container.")

            if not container.can_hold_item(item):
                if container.is_locked():
                    return caller.msg(f"{self.get_display_name(container)} is locked.")

                if container.is_full():
                    return caller.msg(f"{self.get_display_name(container)} is full.")

                if container.is_too_heavy(item):
                    caller.msg(f"{self.get_display_name(container)} is too heavy to hold {self.get_display_name(item)}.")
                    return

                caller.msg(f"You can't store {self.get_display_name(item)} in {self.get_display_name(container)}.")
                return

        item.move_to(container, quiet=True)
        self.send_room_message(
            "$You() $conj(store) $obj(obj) in $obj(container)",
            mapping={"obj": item, "container": container},
            sound="You hear something move."
        )

    def find_suitable_container(self, caller, item):
        """Find the first suitable container in the caller's inventory."""
        for obj in caller.contents:
            if is_container(obj) and obj.can_hold_item(item) and obj != item:
                return obj
        return None
