"""Player command to display in-game time (custom calendar + Gregorian view)."""

from evennia.commands.default.muxcommand import MuxCommand
from evennia.contrib.base_systems import custom_gametime


class CmdTime(MuxCommand):
    """Display the current in-game time.

    Usage:
      time
    """

    key = "time"
    locks = "cmd:all()"

    def func(self):
        # Custom calendar view
        y, mon, d, h, mi, s = custom_gametime.custom_gametime(absolute=True)
        custom_line = (
            f"Custom calendar: Year {y}, Month {mon}, Day {d} — {h:02}:{mi:02}:{s:02}"
        )

        self.caller.msg(custom_line)
