"""EmmeTI Febos sensor definitions."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import FebosConfigEntry, FebosDataUpdateCoordinator


class FebosSensorEntityDescription(SensorEntityDescription):
    """Describes an EmmeTI Febos sensor entity description."""


class FebosSensorEntity(CoordinatorEntity[FebosDataUpdateCoordinator], SensorEntity):
    """Defines an EmmeTI Febos sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FebosDataUpdateCoordinator,
        description: FebosSensorEntityDescription,
        device: dict[str, Any],
        thing: dict[str, Any],
        resource: dict[str, Any],
    ) -> None:
        """Initialize EmmeTI Febos sensor."""
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
    def native_value(self) -> str | None:
        """Return the value of the sensor."""
        return self.value_fn()


async def async_setup_entry(
    hass: HomeAssistant,
    entry: FebosConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a config entry."""
    async_add_entities(
        FebosSensorEntity(
            coordinator=entry.runtime_data,
            description=FebosSensorEntityDescription(
                key=resource["key"],
                native_unit_of_measurement=resource["unit"],
                device_class=resource["class"],
                state_class=resource["state"],
            ),
            device=device,
            thing=thing,
            resource=resource,
        )
        for device, thing, resource in entry.runtime_data.get_sensors()
    )
