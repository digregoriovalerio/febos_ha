"""EmmeTI Febos Binary Sensor definitions."""

from __future__ import annotations

from pprint import pformat
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import FebosConfigEntry, FebosDataUpdateCoordinator


class FebosBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes an EmmeTI Febos binary sensor entity description."""


class FebosBinarySensorEntity(
    CoordinatorEntity[FebosDataUpdateCoordinator], BinarySensorEntity
):
    """Defines an EmmeTI Febos binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FebosDataUpdateCoordinator,
        description: FebosBinarySensorEntityDescription,
        device: dict[str, Any],
        thing: dict[str, Any],
        resource: dict[str, Any],
    ) -> None:
        """Initialize the Sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key
        self._attr_name = resource["name"]
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    device["installation_id"],
                    device["id"],
                    thing["id"],
                )
            },
            entry_type=DeviceEntryType.SERVICE,
            manufacturer=device["manufacturer"],
            model=device["model"],
            name=thing["name"],
        )
        self.value_fn = resource["value_fn"]

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.value_fn()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FebosConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a config entry."""
    async_add_entities(
        FebosBinarySensorEntity(
            coordinator=entry.runtime_data,
            description=FebosBinarySensorEntityDescription(
                key=resource["key"],
                device_class=resource["class"],
            ),
            device=device,
            thing=thing,
            resource=resource,
        )
        for device, thing, resource in entry.runtime_data.get_binary_sensors()
    )
