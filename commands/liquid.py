"""Commands for interacting with LiquidContainerMixin objects."""

from evennia.commands.command import Command
from evennia.utils.utils import inherits_from


class CmdFill(Command):
    """Fill one liquid container from another.

    Usage:
      fill <dest> <source>
    """

    key = "fill"
    locks = "cmd:all()"

    def parse(self):
        parts = self.args.rsplit(" ", 1)
        if len(parts) == 2:
            self.dest_name = parts[0].strip()
            self.source_name = parts[1].strip()
        else:
            self.dest_name = self.args.strip()
            self.source_name = ""

    def func(self):
        if not self.dest_name or not self.source_name:
            self.caller.msg("Usage: fill <dest> <source>")
            return
        dest = self.caller.search(self.dest_name)
        if not dest:
            return
        source = self.caller.search(self.source_name)
        if not source:
            return
        if not (inherits_from(dest, "typeclasses.liquid.LiquidContainerMixin") and inherits_from(source, "typeclasses.liquid.LiquidContainerMixin")):
            self.caller.msg("Both objects must be liquid containers.")
            return
        dest.fill_from_container(source, filler=self.caller)


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
        if not inherits_from(container, "typeclasses.liquid.LiquidContainerMixin"):
            self.caller.msg("You can't empty that.")
            return
        container.empty_liquid(emptier=self.caller)
