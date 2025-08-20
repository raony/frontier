"""Store items in containers.

This command allows characters to store items in containers using the
ContainerMixin functionality.
"""

from .command import Command
from typeclasses.container import is_container
from world.msgs import VisualMsg


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

        item = caller.quiet_search(item_key)
        if not item:
            caller.msg(f"You don't have {item_key}.")
            return

        container = caller.quiet_search(container_key)
        if not container:
            caller.msg(f"You don't see {container_key}.")
            return

        if not is_container(container):
            return caller.msg(f"{container.get_display_name(caller)} is not a container.")

        if container.location != caller.location and container.location != caller:
            return caller.msg(f"You can't reach {container.get_display_name(caller)}.")

        if not container.can_hold_item(item):
            if container.is_container_locked():
                return caller.msg(f"{container.get_display_name(caller)} is locked.")

            if len(container.contents) >= container.get_container_capacity():
                return caller.msg(f"{container.get_display_name(caller)} is full.")

            if hasattr(item, 'weight') and hasattr(container, 'get_container_weight_limit'):
                current_weight = sum(obj.weight for obj in container.contents if hasattr(obj, 'weight'))
                if current_weight + item.weight > container.get_container_weight_limit():
                    caller.msg(f"{container.get_display_name(caller)} is too heavy to hold {item.get_display_name(caller)}.")
                    return

            caller.msg(f"You can't store {item.get_display_name(caller)} in {container.get_display_name(caller)}.")
            return

        item.move_to(container)
        msg_content = "$You() $conj(store) $you(obj) in $you(container)"
        caller.location.msg_contents(
            msg_content,
            from_obj=caller,
            mapping={"obj": item, "container": container},
            msg_obj=VisualMsg(msg_content, sound="You hear something move.").to_dict()
        )
