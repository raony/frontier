"""Builder command to set in-game time using Evennia custom gametime contrib.

Usage:
  @settime YYYY-MM-DD HH:mm:SS

Requires Builder permission. Sets TIME_GAME_EPOCH in live settings via Evennia's
server runtime settings helper and reloads the server to apply immediately.
"""

from __future__ import annotations

from datetime import datetime
import time

from evennia.commands.default.muxcommand import MuxCommand
import os
import re
from django.conf import settings
from evennia.contrib.base_systems import custom_gametime


class CmdSetTime(MuxCommand):
    """Set the current in-game time (Builder-only).

    Syntax:
      @settime YYYY-MM-DD HH:mm:SS
    """

    key = "@settime"
    # Always operate in the custom calendar defined by TIME_UNITS
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        if not args:
            caller.msg("Usage: @settime YYYY-MM-DD HH:mm:SS")
            return
        try:
            dt = datetime.strptime(args, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            caller.msg("Invalid format. Use YYYY-MM-DD HH:mm:SS")
            return

        # Persist by updating TIME_GAME_EPOCH in settings.py and reloading.
        # Compute the epoch needed so that the current time becomes the desired time.
        try:
            # Compute delta using custom calendar seconds
            cy, cmon, cday, chr_, cmin, csec = custom_gametime.custom_gametime(absolute=True)
            units = getattr(settings, "TIME_UNITS", None) or {
                "sec": 1,
                "min": 60,
                "hour": 3600,
                "day": 86400,
                "month": 2592000,
                "year": 31104000,
            }

            def to_seconds(y: int, mon: int, d: int, h: int, mi: int, s: int) -> int:
                # Months and days are 1-indexed in custom calendar
                sec = int(s)
                sec += int(mi) * units["min"]
                sec += int(h) * units["hour"]
                sec += max(int(d) - 1, 0) * units["day"]
                sec += max(int(mon) - 1, 0) * units["month"]
                sec += int(y) * units["year"]
                return sec

            current_game_seconds = to_seconds(cy, cmon, cday, chr_, cmin, csec)
            desired_game_seconds = to_seconds(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            current_epoch = int(getattr(settings, "TIME_GAME_EPOCH", 0) or 0)
            # New epoch so that (current_game_seconds - current_epoch) + new_epoch == desired_game_seconds
            # => new_epoch = current_epoch + (desired - current)
            epoch = current_epoch + (desired_game_seconds - current_game_seconds)
            game_dir = getattr(settings, "GAME_DIR", ".")
            settings_path = os.path.join(game_dir, "server", "conf", "settings.py")

            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()

            if re.search(r"^\s*TIME_GAME_EPOCH\s*=", content, flags=re.M):
                new_content = re.sub(
                    r"^\s*TIME_GAME_EPOCH\s*=.*$",
                    f"TIME_GAME_EPOCH = {epoch}",
                    content,
                    flags=re.M,
                )
            else:
                new_content = content.rstrip() + f"\n\nTIME_GAME_EPOCH = {epoch}\n"

            with open(settings_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            caller.msg(f"In-game time set to {dt:%Y-%m-%d %H:%M:%S}. Reloading server ...")
            # Use in-game reload command to apply new settings
            self.caller.execute_cmd("@reload")
        except Exception as err:
            caller.msg(f"Failed to set game time: {err}")
            return
