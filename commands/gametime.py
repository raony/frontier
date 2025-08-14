"""Player command to describe sun position; show rough hour if skilled."""

from evennia.commands.default.muxcommand import MuxCommand
from evennia.contrib.base_systems import custom_gametime


class CmdTime(MuxCommand):
    """Describe the sun's position; skilled characters estimate the hour.

    Usage:
      time
    """

    key = "time"
    locks = "cmd:all()"

    def func(self):
        _, _, _, hour, minute, _ = custom_gametime.custom_gametime(absolute=True)

        def describe_sun(h: int, m: int) -> str:
            if h < 5 or h >= 20:
                return "The sun is below the horizon."
            if 5 <= h < 7:
                return "The sun is rising over the eastern horizon."
            if 7 <= h < 10:
                return "The sun hangs low in the morning sky."
            if 10 <= h < 14:
                return "The sun stands high overhead."
            if 14 <= h < 18:
                return "The sun drifts west in the afternoon."
            # 18–20
            return "The sun is setting beyond the western horizon."

        def get_skill_level(name: str) -> str:
            obj = self.caller
            if hasattr(obj, "get_skill_level_label"):
                label = obj.get_skill_level_label(name)
                if label and label != "untrained":
                    return label
            return "untrained"

        def approx_time(h: int, m: int, level: str) -> str:
            if level == "untrained":
                return ""
            if level == "novice":
                # nearest 2 hours
                total = h * 60 + m
                rounded = int(round(total / 120.0) * 120) % (24 * 60)
                rh, rm = divmod(rounded, 60)
                return f"You reckon it's around {rh:02}:00."
            if level == "journeyman":
                # nearest hour
                rh = (h + (1 if m >= 30 else 0)) % 24
                return f"You reckon it's about {rh:02}:00."
            # master: nearest half hour
            add = 30 if m >= 45 else (0 if m < 15 else 30)
            total = (h * 60 + ((0 if m < 15 else 30 if m < 45 else 60))) % (24 * 60)
            rh, rm = divmod(total, 60)
            return f"You reckon it's about {rh:02}:{rm:02}."

        sun = describe_sun(hour, minute)
        msg = sun
        # Use snake_case skill key
        level = get_skill_level("time_keeping") or "untrained"
        if level != "untrained":
            msg = f"{sun}\n{approx_time(hour, minute, level)}"

        self.caller.msg(msg)


class CmdSysTime(MuxCommand):
    """Show Evennia's default system/game time table.

    Usage:
      systime
    """

    key = "systime"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        # Defer to Evennia's default time command (usually @time)
        self.caller.execute_cmd("@time")
