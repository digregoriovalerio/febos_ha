"""EmmeTI Febos Binary Sensor definitions."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

# from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import FebosDataUpdateCoordinator
from .parser import FebosDeviceData, FebosResourceData, FebosThingData


class FebosDeviceInfo(DeviceInfo):
    """EmmeTI Febos device info."""

    def __init__(self, device: FebosDeviceData, thing: FebosThingData) -> None:
        """Initialize the device info instance."""
        self.identifiers = {
            (
                DOMAIN,
                device.installation_id,
                device.id,
                thing.id,
            )
        }
        self.entry_type = DeviceEntryType.SERVICE
        self.manufacturer = device.manufacturer
        self.model = device.model
        self.name = thing.name


class FebosBinarySensorEntity(
    CoordinatorEntity[FebosDataUpdateCoordinator], BinarySensorEntity
):
    """Defines an EmmeTI Febos binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FebosDataUpdateCoordinator,
        description: BinarySensorEntityDescription,
        device_info: FebosDeviceInfo,
    ) -> None:
        """Initialize EmmeTI Febos sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key
        self._attr_name = description.resource.name
        self._attr_device_info = device_info

    #    @callback
    #    def _handle_coordinator_update(self) -> None:
    #        """Handle updated data from the coordinator."""
    #        LOGGER.info(f"{self._attr_unique_id}: {self.value_fn()}")
    #        self.async_write_ha_state()
    #        self.coordinator.async_request_refresh()

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        value = self.description.resource.get_value()
        LOGGER.debug(f"{self._attr_unique_id}: {value}")
        return value

    @staticmethod
    def create(
        coordinator: FebosDataUpdateCoordinator,
        device: FebosDeviceData,
        thing: FebosThingData,
        resource: FebosResourceData,
    ):
        """Create the binary sensor entity."""
        return FebosBinarySensorEntity(
            coordinator=coordinator,
            description=BinarySensorEntityDescription(
                key=resource.key, device_class=resource.sensor_class
            ),
            device_info=FebosDeviceInfo(device=device, thing=thing),
        )


class FebosSensorEntity(CoordinatorEntity[FebosDataUpdateCoordinator], SensorEntity):
    """Defines an EmmeTI Febos sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FebosDataUpdateCoordinator,
        description: SensorEntityDescription,
        device_info: FebosDeviceInfo,
    ) -> None:
        """Initialize EmmeTI Febos sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = description.key
        self._attr_name = description.resource.name
        self._attr_device_info = device_info

    #    @callback
    #    def _handle_coordinator_update(self) -> None:
    #        """Handle updated data from the coordinator."""
    #        LOGGER.info(f"{self._attr_unique_id}: {self.value_fn()}")
    #        self.async_write_ha_state()
    #        self.coordinator.async_request_refresh()

    @property
    def native_value(self) -> str | None:
        """Return the value of the sensor."""
        value = self.description.resource.get_value()
        LOGGER.debug(f"{self._attr_unique_id}: {value}")
        return value

    @staticmethod
    def create(
        coordinator: FebosDataUpdateCoordinator,
        device: FebosDeviceData,
        thing: FebosThingData,
        resource: FebosResourceData,
    ):
        """Create the sensor entity."""
        return FebosSensorEntity(
            coordinator=coordinator,
            description=SensorEntityDescription(
                key=resource.key,
                device_class=resource.sensor_class,
                state_class=resource.state_class,
                native_unit_of_measurement=resource.meas_unit,
            ),
            device_info=FebosDeviceInfo(device=device, thing=thing),
        )
