"""EmmeTI Febos data update coordinator."""

from __future__ import annotations

from datetime import timedelta

from febos.api import FebosApi
from febos.errors import AuthenticationError, FebosError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .febos import FebosData

type FebosConfigEntry = ConfigEntry[FebosDataUpdateCoordinator]


class FebosDataUpdateCoordinator(DataUpdateCoordinator):
    """Periodically download the data from the EmmeTI Febos webapp."""

    def __init__(
        self, hass: HomeAssistant, config_entry: FebosConfigEntry, api: FebosApi
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
        self.api = api
        self.data = {}

    def setup_data(self):
        """Set up data from EmmeTI Febos webapp."""
        self.api.login()
        LOGGER.debug("Login successful")
        data = {}
        for inst_id in self.api.login_data.get("installationIdList", []):
            data[inst_id] = {"id": inst_id, "devices": {}, "groups": set()}
            response = self.api.page_config(inst_id)
            for device in response.get("deviceMap", {}).values():
                device = FebosData.parse_device(device)
                device["slaves"] = {}
                device["things"] = {}
                response2 = self.api.get_febos_slave(inst_id, device["id"])
                for slave in response2:
                    slave = FebosData.parse_slave(slave, device)
                    device["slaves"][slave["id"]] = slave
                data[inst_id]["devices"][device["id"]] = device
            for thing in response.get("thingMap", {}).values():
                device_id = thing["deviceId"]
                thing = FebosData.parse_thing(thing)
                data[inst_id]["devices"][device_id]["things"][thing["id"]] = thing
            for page in response.get("pageMap", {}).values():
                for tab in page.get("tabList", []):
                    for widget in tab.get("widgetList", []):
                        for group in widget.get("widgetInputGroupList", []):
                            group_code = group["inputGroupGetCode"]
                            data[inst_id]["groups"].add(group_code)
                            for resource in group.get("inputList", []):
                                resource = FebosData.parse_resource(
                                    resource, inst_id, group_code
                                )
                                if resource is not None:
                                    data[inst_id]["devices"][group["deviceId"]][
                                        "things"
                                    ][group["thingId"]]["resources"][
                                        resource["id"]
                                    ] = resource
        self.data = data
        LOGGER.debug("Setup complete")

    def _fetch_data(self):
        """Update data from EmmeTI Febos webapp."""
        for inst_id, installation in self.data.items():
            response = self.api.realtime_data(inst_id, self.data[inst_id]["groups"])
            for entry in response:
                for code, value in entry["data"].items():
                    value = FebosData.parse_value(value["i"], code)
                    self.data[inst_id]["devices"][entry["deviceId"]]["things"][
                        entry["thingId"]
                    ]["resources"][code]["value"] = value
            for device_id, device in installation["devices"].items():
                response = self.api.get_febos_slave(inst_id, device_id)
                for slave in response:
                    for code, value in slave.items():
                        value = FebosData.parse_value(value, code)
                        resources = device["slaves"][slave["indirizzoSlave"]][
                            "resources"
                        ]
                        if code in resources:
                            resources[code]["value"] = value
        LOGGER.debug("Data update")

    def fetch_data(self):
        """Update data from EmmeTI Febos webapp handling reauthentication."""
        try:
            self._fetch_data()
        except AuthenticationError as e:
            LOGGER.debug(str(e))
            self.api.login()
            LOGGER.debug("Login successful")
            self._fetch_data()

    def get_sensors(self):
        """List all EmmeTI Febos sensors."""
        for installation in self.data.values():
            for device in installation["devices"].values():
                for thing in device["things"].values():
                    for resource in thing["resources"].values():
                        if (
                            resource["type"] == Platform.SENSOR
                            and resource["value"] is not None
                        ):
                            yield device, thing, resource
                for slave in device["slaves"].values():
                    for resource in slave["resources"].values():
                        if (
                            resource["type"] == Platform.SENSOR
                            and resource["value"] is not None
                        ):
                            yield device, slave, resource

    def get_binary_sensors(self):
        """List all EmmeTI Febos binary sensors."""
        for installation in self.data.values():
            for device in installation["devices"].values():
                for thing in device["things"].values():
                    for resource in thing["resources"].values():
                        if (
                            resource["type"] == Platform.BINARY_SENSOR
                            and resource["value"] is not None
                        ):
                            yield device, thing, resource
                for slave in device["slaves"].values():
                    for resource in slave["resources"].values():
                        if (
                            resource["type"] == Platform.BINARY_SENSOR
                            and resource["value"] is not None
                        ):
                            yield device, slave, resource

    async def _async_setup(self):
        """Set up the coordinator."""
        try:
            await self.hass.async_add_executor_job(self.setup_data)
        except FebosError as e:
            LOGGER.error(str(e))
            raise ConfigEntryAuthFailed from e

    async def _async_update_data(self) -> FebosData:
        """Async update wrapper."""
        try:
            await self.hass.async_add_executor_job(self.fetch_data)
        except FebosError as e:
            LOGGER.error(str(e))
            raise ConfigEntryAuthFailed from e
        return self.data
