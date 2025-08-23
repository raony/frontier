from .command import Command

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
