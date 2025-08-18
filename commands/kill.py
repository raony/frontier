"""Kill command for testing living/dead state transitions."""

from evennia.commands.default.muxcommand import MuxCommand


class CmdKill(MuxCommand):
    """Kill a living being for testing purposes.

    Usage:
      @kill <target>
      @kill <target> = <reason>

    Target can be:
      - A character name
      - "self" or "me" (targets yourself)
      - A database reference like "#1"

    This command kills a living being, setting their state to dead.
    Only available to builders for testing purposes.
    """

    key = "@kill"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: @kill <target> [= <reason>]")
            return

        # Parse arguments
        if "=" in self.args:
            target_name, reason = self.args.split("=", 1)
            target_name = target_name.strip()
            reason = reason.strip()
        else:
            target_name = self.args.strip()
            reason = "Killed by builder for testing"

                # Find the target using caller.search (handles self, me, #dbref, etc.)
        target = caller.search(target_name, location=caller.location)
        if not target:
            return

        # Check if target is a living being
        if not hasattr(target, 'is_living_being'):
            caller.msg(f"{target.get_display_name(caller)} is not a living being.")
            return

        # Check if already dead
        if target.is_dead():
            caller.msg(f"{target.get_display_name(caller)} is already dead.")
            return

        # Kill the target - use proper death method
        target.at_death()

        # Notify everyone in the room
        caller.msg(f"You kill {target.get_display_name(caller)}. {reason}")
        target.msg(f"You have been killed by {caller.get_display_name(target)}. {reason}")

        # Notify others in the room
        for obj in caller.location.contents:
            if obj != caller and obj != target and hasattr(obj, 'msg'):
                obj.msg(f"{caller.get_display_name(obj)} kills {target.get_display_name(obj)}. {reason}")


class CmdRevive(MuxCommand):
    """Revive a dead living being for testing purposes.

    Usage:
      @revive <target>
      @revive <target> = <reason>

    Target can be:
      - A character name
      - "self" or "me" (targets yourself)
      - A database reference like "#1"

    This command revives a dead living being, setting their state to alive.
    Only available to builders for testing purposes.
    """

    key = "@revive"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller

        if not self.args:
            caller.msg("Usage: @revive <target> [= <reason>]")
            return

        # Parse arguments
        if "=" in self.args:
            target_name, reason = self.args.split("=", 1)
            target_name = target_name.strip()
            reason = reason.strip()
        else:
            target_name = self.args.strip()
            reason = "Revived by builder for testing"

                        # Find the target using caller.search (handles self, me, #dbref, etc.)
        target = caller.search(target_name, location=caller.location)
        if not target:
            return

        # Check if target is a living being
        if not hasattr(target, 'is_living_being'):
            caller.msg(f"{target.get_display_name(caller)} is not a living being.")
            return

        # Check if already alive
        if target.is_living():
            caller.msg(f"{target.get_display_name(caller)} is already alive.")
            return

        # Revive the target using the helper method
        self._revive_target(target)

        # Notify everyone in the room
        caller.msg(f"You revive {target.get_display_name(caller)}. {reason}")
        target.msg(f"You have been revived by {caller.get_display_name(target)}. {reason}")

        # Notify others in the room
        for obj in caller.location.contents:
            if obj != caller and obj != target and hasattr(obj, 'msg'):
                obj.msg(f"{caller.get_display_name(obj)} revives {target.get_display_name(obj)}. {reason}")

    def _revive_target(self, target):
        """Helper method to revive a target. Can be reused by other commands."""
        # Use the new living module revive method
        target.revive()
