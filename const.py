"""EmmeTI Febos Constants."""

import logging

from homeassistant.const import Platform

DOMAIN = "febos"

LOGGER = logging.getLogger(__package__)
PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]
