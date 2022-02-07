"""Constants for Gecko."""

from geckolib import VERSION as GECKOLIB_VERSION

# Base component constants
NAME = "Gecko"
DOMAIN = "gecko"
DOMAIN_DATA = f"{DOMAIN}_data"
# TODO: Find a way to DRY this const with the one in manifest.json
VERSION = "0.0.11"

ISSUE_URL = "https://github.com/gazoodle/gecko-home-assistant/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
FAN = "fan"
SENSOR = "sensor"
SWITCH = "switch"
CLIMATE = "climate"
LIGHT = "light"
PLATFORMS = [BINARY_SENSOR, FAN, SENSOR, SWITCH, CLIMATE, LIGHT]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_SPA_NAME = "spaname"
CONF_SPA_IDENTIFIER = "spaidentifier"
CONF_SPA_ADDRESS = "spaipaddress"

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

# GECKOLIB constants
GECKOLIB_MANAGER_UUID = "cc927d39-a1c3-449b-a740-50393cd2699f"
