from commands.command import Command


class CmdRest(Command):
    """Toggle resting to recover tiredness."""

    key = "rest"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        # Check capability rather than inheritance path to support mixin composition
        if not hasattr(caller, "is_resting"):
            caller.msg("You can't rest.")
            return
        if caller.is_resting:
            caller.msg("You are already resting. Use 'stand' to get up.")
            return
        caller.is_resting = True
        caller.msg("You settle down to rest.")
        location = caller.location
        if location:
            location.msg_contents(
                f"{caller.get_display_name(location)} lies down to rest.",
                exclude=caller,
            )
