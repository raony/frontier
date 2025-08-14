"""Hold and release items in hands.

Holdables are separate from equippable wear slots. Items must have
`db.is_holdable=True` (e.g., via `HoldableMixin`) to be held.
"""

from .command import Command


class CmdHold(Command):
    """Hold a carried item in your hand.

    Usage:
      hold <item>
    """

    key = "hold"
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Hold what?")
            return
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        if not hasattr(caller, "hold"):
            caller.msg("You can't hold things.")
            return
        caller.hold(obj)


class CmdRelease(Command):
    """Release a held item from your hand(s).

    Usage:
      release <item>
      release all
      unhold <item>
    """

    key = "release"
    aliases = ["unhold"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not hasattr(caller, "release"):
            caller.msg("You can't release held items.")
            return
        if not self.args:
            caller.msg("Release what? Specify an item or 'all'.")
            return
        # Try 'all'
        if self.args.strip().lower() == "all":
            caller.release("all")
            return
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        caller.release(obj)
