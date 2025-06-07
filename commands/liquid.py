"""Commands for interacting with LiquidContainerMixin objects."""

from evennia.commands.command import Command


class CmdFill(Command):
    """Fill a container with a liquid.

    Usage:
      fill <container>=<liquid>
    """

    key = "fill"
    locks = "cmd:all()"

    def parse(self):
        if "=" in self.args:
            container, liquid = [part.strip() for part in self.args.split("=", 1)]
        else:
            container, liquid = self.args.strip(), ""
        self.container_name = container
        self.liquid = liquid

    def func(self):
        if not self.container_name:
            self.caller.msg("Fill what?")
            return
        container = self.caller.search(self.container_name)
        if not container:
            return
        if not hasattr(container, "fill_liquid"):
            self.caller.msg("You can't fill that.")
            return
        if not self.liquid:
            self.caller.msg("Fill it with what?")
            return
        container.fill_liquid(self.liquid, filler=self.caller)


class CmdEmpty(Command):
    """Empty a liquid container.

    Usage:
      empty <container>
    """

    key = "empty"
    locks = "cmd:all()"

    def parse(self):
        self.container_name = self.args.strip()

    def func(self):
        if not self.container_name:
            self.caller.msg("Empty what?")
            return
        container = self.caller.search(self.container_name)
        if not container:
            return
        if not hasattr(container, "empty_liquid"):
            self.caller.msg("You can't empty that.")
            return
        container.empty_liquid(emptier=self.caller)
