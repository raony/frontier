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


class CmdLight(Command):
    """Light a torch or other consumable light source you carry.

    Usage:
      light <item>
      ignite <item>
    """

    key = "light"
    aliases = ["ignite"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Light what?")
            return
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        if not hasattr(obj, "turn_on"):
            caller.msg("You can't light that.")
            return
        obj.turn_on(caller=caller)


class CmdExtinguish(Command):
    """Extinguish a lit item.

    Usage:
      extinguish <item>
      douse <item>
      putout <item>
    """

    key = "extinguish"
    aliases = ["douse", "putout", "putoff"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Extinguish what?")
            return
        obj = caller.search(self.args, candidates=caller.contents)
        if not obj:
            return
        if not hasattr(obj, "turn_off"):
            caller.msg("You can't extinguish that.")
            return
        obj.turn_off(caller=caller)


class CmdDarkvision(Command):
    """Toggle darkvision for builders to see in dark areas.

    Usage:
      darkvision
    """

    key = "darkvision"
    locks = "cmd:perm(Builder)"

    def func(self):
        caller = self.caller
        if not hasattr(caller, "light_threshold"):
            caller.msg("You don't have light perception.")
            return

        current = int(caller.light_threshold or 20)
        if current > 0:
            # Enable darkvision by setting threshold to 0
            caller.light_threshold = 0
            caller.msg("Darkvision enabled. You can now see in complete darkness.")
        else:
            # Disable darkvision by restoring normal threshold
            caller.light_threshold = 20
            caller.msg("Darkvision disabled. You now require light to see.")
