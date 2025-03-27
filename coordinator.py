"""EmmeTI Febos data update coordinator."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .parser import (
    FebosClient,
    FebosDeviceData,
    FebosInstallationData,
    FebosResourceData,
    FebosThingData,
)

type FebosConfigEntry = ConfigEntry[FebosDataUpdateCoordinator]


class FebosDataUpdateCoordinator(DataUpdateCoordinator):
    """Periodically download the data from the EmmeTI Febos webapp."""

    data: list[FebosInstallationData]

    def __init__(
        self, hass: HomeAssistant, config_entry: FebosConfigEntry, client: FebosClient
    ) -> None:
        """Initialize the data service."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
            always_update=False,
        )
        self.client = client

    def _setup(self):
        """Set up data from EmmeTI Febos webapp."""
        self.client.get_resources()

    def _update_data(self):
        """Update data from EmmeTI Febos webapp."""
        self.client.update_values()
        return self.client.resources

    def get_entities(
        self, entity_type: Platform
    ) -> tuple[FebosDeviceData, FebosThingData, FebosResourceData]:
        """List all EmmeTI Febos entities of a given type."""
        return [
            (d, t, r)
            for i in self.client.resources
            for d in i.devices.values()
            for t in list(d.things.values()) + list(d.slaves.values())
            for r in t.resources.values()
            if (r.type == entity_type and r.value is not None)
        ]

    async def _async_setup(self):
        """Set up the coordinator."""
        await self.hass.async_add_executor_job(self._setup)

    async def _async_update_data(self) -> dict[str, FebosInstallationData]:
        """Async update wrapper."""
        return await self.hass.async_add_executor_job(self._update_data)
