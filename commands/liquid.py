"""Commands for interacting with LiquidContainerMixin objects."""

from evennia.commands.command import Command


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
        dest_candidates = self.caller.search(
            self.dest_name,
            quiet=True,
            typeclass="typeclasses.liquid.LiquidContainerMixin",
        )
        if not dest_candidates:
            return
        source_candidates = self.caller.search(
            self.source_name,
            quiet=True,
            typeclass="typeclasses.liquid.LiquidContainerMixin",
        )
        if not source_candidates:
            return
        dest = dest_candidates[0]
        source = source_candidates[0]
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
        container_candidates = self.caller.search(
            self.container_name,
            quiet=True,
            typeclass="typeclasses.liquid.LiquidContainerMixin",
        )
        if not container_candidates:
            return
        container = container_candidates[0]
        container.empty_liquid(emptier=self.caller)
