r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

# Register world app for custom database models
INSTALLED_APPS += ["world"]

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "frontier"


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

######################################################################
# Game time configuration
######################################################################

# In-game time runs 6× faster than real time (1 real hour = 6 in-game hours)
TIME_FACTOR = 6.0

# Optional: Define a custom epoch for game time (None uses real epoch)
# TIME_GAME_EPOCH = None

# Enable custom gametime calendar (Evennia contrib) — example Shire-like calendar
# Adjust as needed. Units must be multiples of the previous one.
TIME_UNITS = {
    "sec": 1,
    "min": 60,
    "hour": 60 * 60,
    "day": 60 * 60 * 24,
    "month": 60 * 60 * 24 * 30,
    "year": 60 * 60 * 24 * 30 * 12,
}
TIME_GAME_EPOCH = 1753653987
