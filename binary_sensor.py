"""EmmeTI Febos Binary Sensor definitions."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import LOGGER
from .coordinator import FebosConfigEntry
from .febos import FebosBinarySensorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FebosConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a config entry."""
    LOGGER.debug("Loading binary sensors")
    async_add_entities(
        FebosBinarySensorEntity.create(
            coordinator=entry.runtime_data,
            device=d,
            thing=t,
            resource=r,
        )
        for d, t, r in entry.runtime_data.get_entities(Platform.BINARY_SENSOR)
    )
