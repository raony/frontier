from .command import Command

class CmdExamine(Command):
    """
    Examine a target in detail.

    Usage:
      examine <target>

    Shows a detailed description of the target, using its return_appearance with examine=True.
    """

    key = "examine"
    aliases = ["ex"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        target = self.lhs
        if not target:
            target = caller.location
        else:
            target = caller.quiet_search(target)

        if not target:
            caller.msg(f"You can't find {target}.")
            return

        caller.msg(target.return_appearance(caller, examine=True))
