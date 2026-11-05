"""Constants for Gecko."""

import json
import pathlib

from geckolib import VERSION as GECKOLIB_VERSION

# Base component constants, some loaded directly from the manifest
_LOADER_PATH = pathlib.Path(__loader__.path)
_MANIFEST_PATH = _LOADER_PATH.parent / "manifest.json"
with pathlib.Path.open(_MANIFEST_PATH, encoding="Latin1") as json_file:
    data = json.load(json_file)
NAME = f"{data['name']}"
DOMAIN = f"{data['domain']}"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = f"{data['version']}"
ISSUE_URL = f"{data['issue_tracker']}"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
BUTTON = "button"
FAN = "fan"
SENSOR = "sensor"
SWITCH = "switch"
CLIMATE = "climate"
LIGHT = "light"
SELECT = "select"
WATER_HEATER = "water_heater"
DATE = "date"
NUMBER = "number"
PLATFORMS = [
    BINARY_SENSOR,
    BUTTON,
    FAN,
    SENSOR,
    SWITCH,
    CLIMATE,
    LIGHT,
    SELECT,
    WATER_HEATER,
    DATE,
    NUMBER,
]

# Option keys
SHOW_PING_KEY = "show_ping"

# Configuration and options
CONF_SPA_NAME = "spaname"
CONF_SPA_IDENTIFIER = "spaidentifier"
CONF_SPA_ADDRESS = "spaipaddress"
CONF_CLIENT_ID = "clientid"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
Gecko Lib: {GECKOLIB_VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""

# Error handling
ERROR_COUNT_TOLERANCE = 5
