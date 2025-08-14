"""Hex map commands for linking rooms to macro hex tiles and querying weather."""

from evennia.commands.default.muxcommand import MuxCommand


class CmdSetHex(MuxCommand):
    """Link the current room to a hex tile by cube coordinates.

    Usage:
      @sethex <q> <r> <s>
    """

    key = "@sethex"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: @sethex <q> <r> <s>")
            return
        room = caller.location
        if not room:
            caller.msg("You are nowhere.")
            return
        try:
            qrs = self.args.strip().split()
            if len(qrs) != 3:
                raise ValueError
            q, r, s = (int(qrs[0]), int(qrs[1]), int(qrs[2]))
        except Exception:
            caller.msg("Invalid coordinates. Usage: @sethex <q> <r> <s>")
            return
        try:
            tile = room.set_hex_by_coords(q, r, s)
            tq, tr, ts = (tile.db.q, tile.db.r, tile.db.s)
            terr = getattr(tile.db, "terrain", "plain")
            caller.msg(f"Linked room to hex {tile.dbref} q={tq}, r={tr}, s={ts} (terrain={terr}).")
        except Exception as err:
            caller.msg(f"Failed to link hex: {err}")


class CmdWeather(MuxCommand):
    """Show current macro weather for this room (from its hex).

    Builder-only helper.
    """

    key = "@weather"
    aliases = ["@wx"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        room = caller.location
        if not room:
            caller.msg("You are nowhere.")
            return
        wx = "clear"
        if hasattr(room, "get_hex_weather"):
            wx = room.get_hex_weather()
        tile = room.get_hex_tile() if hasattr(room, "get_hex_tile") else None
        if tile:
            q, r, s = (tile.db.q, tile.db.r, tile.db.s)
            caller.msg(f"Weather here is {wx} (hex {tile.dbref} q={q}, r={r}, s={s}).")
        else:
            caller.msg(f"Weather here is {wx}.")
