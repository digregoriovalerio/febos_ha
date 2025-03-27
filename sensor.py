"""EmmeTI Febos sensor definitions."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import LOGGER
from .coordinator import FebosConfigEntry
from .febos import FebosSensorEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FebosConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a config entry."""
    LOGGER.debug("Loading sensors")
    async_add_entities(
        FebosSensorEntity.create(
            coordinator=entry.runtime_data,
            device=d,
            thing=t,
            resource=r,
        )
        for d, t, r in entry.runtime_data.get_entities(Platform.SENSOR)
    )
