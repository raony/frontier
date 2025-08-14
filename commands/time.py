"""Builder commands to set in-game date/time using custom gametime.

Usage:
  @setdatetime YYYY-MM-DD HH:mm:SS   # set current in-game datetime
  @settime HH:mm:SS                  # set current in-game time (same day)

Requires Builder permission. These adjust TIME_GAME_EPOCH and reload the server
so the new in-game time takes effect immediately under the custom calendar.
"""

from __future__ import annotations

from datetime import datetime
import time

from evennia.commands.default.muxcommand import MuxCommand
import os
import re
from django.conf import settings
from evennia.contrib.base_systems import custom_gametime


class CmdSetDateTime(MuxCommand):
    """Set the current in-game date and time (Builder-only).

    Syntax:
      @setdatetime YYYY-MM-DD HH:mm:SS
    """

    key = "@setdatetime"
    # Always operate in the custom calendar defined by TIME_UNITS
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        if not args:
            caller.msg("Usage: @setdatetime YYYY-MM-DD HH:mm:SS")
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


class CmdSetTime(MuxCommand):
    """Set the current in-game time (same day) (Builder-only).

    Syntax:
      @settime HH:mm:SS
    """

    key = "@settime"
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        if not args:
            caller.msg("Usage: @settime HH:mm:SS")
            return
        try:
            # Parse only time; we'll combine with current in-game date
            t_only = datetime.strptime(args, "%H:%M:%S").time()
        except ValueError:
            caller.msg("Invalid format. Use HH:mm:SS")
            return

        # Compute epoch delta using custom calendar (keep same date)
        try:
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
                sec = int(s)
                sec += int(mi) * units["min"]
                sec += int(h) * units["hour"]
                sec += max(int(d) - 1, 0) * units["day"]
                sec += max(int(mon) - 1, 0) * units["month"]
                sec += int(y) * units["year"]
                return sec

            current_game_seconds = to_seconds(cy, cmon, cday, chr_, cmin, csec)
            desired_game_seconds = to_seconds(cy, cmon, cday, t_only.hour, t_only.minute, t_only.second)
            current_epoch = int(getattr(settings, "TIME_GAME_EPOCH", 0) or 0)
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

            # Remove scheduled sunrise/sunset so they reschedule cleanly after reload
            from evennia.scripts.models import ScriptDB as _ScriptDB
            for key in ("at sunrise", "at sunset"):
                try:
                    for scr in _ScriptDB.objects.filter(db_key=key):
                        scr.stop()
                        scr.delete()
                except Exception:
                    pass

            caller.msg(
                f"In-game time set to {t_only.strftime('%H:%M:%S')} (same day). Reloading server ..."
            )
            self.caller.execute_cmd("@reload")
        except Exception as err:
            caller.msg(f"Failed to set time: {err}")
            return
