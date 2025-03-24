"""EmmeTI Febos integration for Home Assistant."""

from febos.api import FebosApi
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import PLATFORMS
from .coordinator import FebosConfigEntry, FebosDataUpdateCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: FebosConfigEntry) -> bool:
    """Set up EmmeTI Febos API from a config entry."""
    api = FebosApi(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
    entry.runtime_data = FebosDataUpdateCoordinator(hass, entry, api)
    await entry.runtime_data.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: FebosConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
