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
    """

    key = "store"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller

        if not self.switches:
            caller.msg("Usage: store/<container> <item>")
            return

        container_key = self.switches[0]
        item_key = self.lhs

        if not item_key:
            caller.msg("Store what?")
            return

        if not container_key:
            caller.msg("Store in what?")
            return

        item = caller.search_item(item_key)
        if not item:
            caller.msg(f"You don't have {item_key}.")
            return

        container = caller.search_item(container_key)
        if not container:
            caller.msg(f"You don't see {container_key}.")
            return

        if not is_container(container):
            return caller.msg(f"{self.get_display_name(container)} is not a container.")

        if container.location != caller.location and container.location != caller:
            return caller.msg(f"You can't reach {self.get_display_name(container)}.")

        if not container.can_hold_item(item):
            if container.is_container_locked():
                return caller.msg(f"{self.get_display_name(container)} is locked.")

            if len(container.contents) >= container.get_container_capacity():
                return caller.msg(f"{self.get_display_name(container)} is full.")

            if hasattr(item, 'weight') and hasattr(container, 'get_container_weight_limit'):
                current_weight = sum(obj.weight for obj in container.contents if hasattr(obj, 'weight'))
                if current_weight + item.weight > container.get_container_weight_limit():
                    caller.msg(f"{self.get_display_name(container)} is too heavy to hold {self.get_display_name(item)}.")
                    return

            caller.msg(f"You can't store {self.get_display_name(item)} in {self.get_display_name(container)}.")
            return

        item.move_to(container)
        self.send_room_message(
            "$You() $conj(store) $you(obj) in $you(container)",
            mapping={"obj": item, "container": container},
            sound="You hear something move."
        )
