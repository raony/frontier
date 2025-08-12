"""Builder commands to create and manage room resources."""

from typing import Optional

from evennia import create_object
from evennia.utils.utils import make_iter

from .command import Command


class CmdCreateResource(Command):
    """Create a resource in your current room.

    Usage:
      createresource <key>[/kind] [= abundance,quality]

    Examples:
      @createresource berry-bush/foraging = 5,2
      @createresource herb-patch/foraging
    """

    key = "createresource"
    aliases = ["@createresource"]
    locks = "cmd:perm(Builders) or perm(Developer) or perm(Admin)"

    def func(self):
        caller = self.caller
        if not caller.location:
            caller.msg("You are nowhere; cannot create a resource.")
            return

        if not self.args:
            caller.msg("Usage: createresource <key>[/kind] [= abundance,quality]")
            return

        key_part, abq_part = (self.args.split("=", 1) + [""])[:2]
        key_part = key_part.strip()
        abq_part = abq_part.strip()

        if "/" in key_part:
            key, kind = [p.strip() for p in key_part.split("/", 1)]
        else:
            key, kind = key_part, "foraging"

        abundance, quality = 5, 1
        if abq_part:
            parts = [p.strip() for p in abq_part.split(",")]
            if parts:
                try:
                    abundance = int(parts[0])
                except (TypeError, ValueError):
                    pass
            if len(parts) > 1:
                try:
                    quality = int(parts[1])
                except (TypeError, ValueError):
                    pass

        try:
            res = create_object("typeclasses.resources.Resource", key=key, location=caller.location)
        except Exception as err:  # pragma: no cover
            caller.msg(f"Could not create resource: {err}")
            return

        res.db.kind = kind
        res.db.abundance = abundance
        res.db.quality = quality
        # Ensure tags reflect kind
        res.tags.add(f"resource:{kind}", category="system")

        caller.msg(f"Created resource '{res.key}' (kind={kind}, abundance={abundance}, quality={quality}).")
