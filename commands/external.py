"""Builder helpers for external rooms (sunlight-enabled)."""

from evennia.commands.default.muxcommand import MuxCommand


class CmdMakeExternal(MuxCommand):
    """Convert the current room into an ExternalRoom and tag it.

    Usage:
      @makeexternal
    """

    key = "@makeexternal"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        room = caller.location
        if not room:
            caller.msg("You are nowhere.")
            return
        try:
            if not room.is_typeclass("typeclasses.rooms.ExternalRoom", exact=False):
                room.swap_typeclass("typeclasses.rooms.ExternalRoom", clean_attributes=False, no_default=True)
            # Ensure tag used by sunrise/sunset filtering
            room.tags.add("external", category="environment")
            caller.msg("This room is now external (sunlight-enabled).")
        except Exception as err:
            caller.msg(f"Failed to convert room: {err}")
