"""EmmeTI Febos helpers for Home Assistant integration."""

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    Platform,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)

from .const import DOMAIN, LOGGER

SLAVE_RESOURCE_MAPPING = {
    "callTemp": {
        "id": "S01",
        "name": "Chiamata Temperatura",
        "type": Platform.BINARY_SENSOR,
        "class": BinarySensorDeviceClass.HEAT,
    },
    "callHumid": {
        "id": "S02",
        "name": "Chiamata Umidità",
        "type": Platform.BINARY_SENSOR,
        "class": BinarySensorDeviceClass.HEAT,
    },
    "stagione": {
        "id": "S03",
        "name": "Stagione",
        "type": Platform.BINARY_SENSOR,
        "class": BinarySensorDeviceClass.COLD,
    },
    "setTemp": {
        "id": "S04",
        "name": "Set Temperatura",
        "type": Platform.SENSOR,
        "class": SensorDeviceClass.TEMPERATURE,
        "state": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
    },
    "temp": {
        "id": "S05",
        "name": "Temperatura",
        "type": Platform.SENSOR,
        "class": SensorDeviceClass.TEMPERATURE,
        "state": SensorStateClass.MEASUREMENT,
        "unit": UnitOfTemperature.CELSIUS,
    },
    "humid": {
        "id": "S06",
        "name": "Umidità",
        "type": Platform.SENSOR,
        "class": SensorDeviceClass.HUMIDITY,
        "state": SensorStateClass.MEASUREMENT,
        "unit": PERCENTAGE,
    },
    "confort": {
        "id": "S07",
        "name": "Comfort",
        "type": Platform.BINARY_SENSOR,
        "class": BinarySensorDeviceClass.PRESENCE,
    },
}


def resource_key(
    installation_id: int,
    group_code: str,
    device_id: int,
    thing_id: int,
    code: str,
) -> str:
    """Return a unique identifier for a resource."""
    return f"{DOMAIN}_{installation_id}_{device_id}_{thing_id}_{code.lower()}"


def slave_resource_key(
    installation_id: int,
    device_id: int,
    slave_addr: int,
    key: str,
) -> str:
    """Return a unique identifier for a slave resource."""
    return f"{DOMAIN}_{installation_id}_{device_id}_{slave_addr}_{key.lower()}"


def parse_group_code(code: str) -> str:
    """Normalize group code."""
    return code.split("@")[0].lower().replace("-", "_")


def parse_sensor_name(name: str) -> str:
    """Normalize sensor name."""
    name = name.replace(" (in KW)", "")
    return name if len(name) > 0 else "Unknown"


def measurement_unit(meas_unit):
    """Return the measurement unit as a Home Assistant enum."""
    return {
        "kW": UnitOfPower.KILO_WATT,
        "°C": UnitOfTemperature.CELSIUS,
        "°": UnitOfTemperature.CELSIUS,
        "h": UnitOfTime.HOURS,
        "HH:mm": UnitOfTime.MINUTES,
        "watt/h": UnitOfEnergy.WATT_HOUR,
        "L/h": UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        "%": PERCENTAGE,
    }.get(meas_unit)


def sensor_class(meas_unit):
    """Return the sensor class."""
    return {
        "kW": SensorDeviceClass.POWER,
        "°C": SensorDeviceClass.TEMPERATURE,
        "°": SensorDeviceClass.TEMPERATURE,
        "h": SensorDeviceClass.DURATION,
        "HH:mm": SensorDeviceClass.DURATION,
        "watt/h": SensorDeviceClass.ENERGY,
        "L/h": SensorDeviceClass.VOLUME_FLOW_RATE,
        "%": SensorDeviceClass.HUMIDITY,
        " ": SensorDeviceClass.ENUM,
        "": SensorDeviceClass.ENUM,
    }.get(meas_unit)


def state_class(sens_class):
    """Return the state class."""
    {
        SensorDeviceClass.ENERGY: SensorStateClass.TOTAL,
        SensorDeviceClass.TIMESTAMP: None,
    }.get(sens_class, SensorStateClass.MEASUREMENT)


def sensor_value(res):
    """Return the sensor value."""
    if res["value"] is None:
        return None
    return res["value"]


def binary_sensor_value(res):
    """Return the binary sensor value."""
    if res["value"] is None:
        return None
    if res["class"] in [
        BinarySensorDeviceClass.COLD,
        BinarySensorDeviceClass.PRESENCE,
    ]:
        return not bool(res["value"])
    return bool(res["value"])


def binary_sensor_class(code):
    """Return the binary sensor class."""
    sens_class = {
        "R8683": BinarySensorDeviceClass.COLD,
        "R16385": BinarySensorDeviceClass.COLD,
        "R9089": BinarySensorDeviceClass.PROBLEM,
        "R9090": BinarySensorDeviceClass.PROBLEM,
        "R9095": BinarySensorDeviceClass.PROBLEM,
        "R9096": BinarySensorDeviceClass.PROBLEM,
        "R9097": BinarySensorDeviceClass.PROBLEM,
        "R9098": BinarySensorDeviceClass.PROBLEM,
        "R9099": BinarySensorDeviceClass.PROBLEM,
        "R9102": BinarySensorDeviceClass.PROBLEM,
        "R9103": BinarySensorDeviceClass.PROBLEM,
        "R9104": BinarySensorDeviceClass.PROBLEM,
        "R16384": BinarySensorDeviceClass.RUNNING,
        "R8681": BinarySensorDeviceClass.RUNNING,
        "R8682": BinarySensorDeviceClass.RUNNING,
        "R8692": BinarySensorDeviceClass.RUNNING,
        "R9072": BinarySensorDeviceClass.RUNNING,
        "R9073": BinarySensorDeviceClass.RUNNING,
        "R9074": BinarySensorDeviceClass.RUNNING,
        "R8672": BinarySensorDeviceClass.WINDOW,
        "R8673": BinarySensorDeviceClass.PRESENCE,
        "R8676": BinarySensorDeviceClass.PRESENCE,
    }.get(code)
    if sens_class is None:
        LOGGER.warning(f"Unsupported sensor class for {code}")
    return sens_class


class FebosData:
    """Parser for EmmeTI Febos webapp data."""

    @staticmethod
    def parse_device(device):
        """Parse an EmmeTI Febos device."""
        dev = {
            "id": device["id"],
            "installation_id": device["installationId"],
            "manufacturer": device["tenantName"],
            "model": device["modelName"],
            "name": f"{device['tenantName']} {device['modelName']} {device['deviceTypeName'].capitalize()}",
        }
        LOGGER.debug(f"[DEVICE][{device['id']}] {dev})")
        return dev

    @staticmethod
    def parse_slave(slave, device):
        """Parse an EmmeTI Febos slave."""
        slv = {
            "id": slave["indirizzoSlave"],
            "name": f"{device['model']} Slave {slave['indirizzoSlave']}",
            "resources": {},
        }
        for k in slave:
            if k in SLAVE_RESOURCE_MAPPING:
                sensor = SLAVE_RESOURCE_MAPPING.get(k).copy()
                sensor["key"] = slave_resource_key(
                    device["installation_id"], device["id"], slave["indirizzoSlave"], k
                )
                sensor["value"] = None
                if sensor["type"] == Platform.BINARY_SENSOR:
                    sensor["value_fn"] = lambda s=sensor: binary_sensor_value(s)
                    LOGGER.debug(f"[BINARY_SENSOR][{sensor['key']}] {sensor}")
                else:
                    sensor["value_fn"] = lambda s=sensor: sensor_value(s)
                    LOGGER.debug(f"[SENSOR][{sensor['key']}] {sensor}")
                slv["resources"][k] = sensor
        return slv

    @staticmethod
    def parse_thing(thing):
        """Parse an EmmeTI Febos thing."""
        thg = {"id": thing["id"], "name": thing["modelName"], "resources": {}}
        LOGGER.debug(f"[THING][{thing['id']}] {thg}")
        return thg

    @staticmethod
    def parse_resource(
        resource,
        installation_id,
        group_code,
    ):
        """Parse an EmmeTI Febos resource."""
        # if resource["code"] in ["R8750", "R8751", "R8752", "R8753", "R8754", "R8755"]:
        #    LOGGER.warning(resource)
        #    return None
        group_code = parse_group_code(group_code)
        key = resource_key(
            installation_id,
            group_code,
            resource["deviceId"],
            resource["thingId"],
            resource["code"],
        )
        name = parse_sensor_name(resource.get("label", ""))
        input_type = resource.get("inputType")
        if input_type == "BOOL":
            sens_class = binary_sensor_class(resource.get("code"))
            sensor = {
                "id": resource["code"],
                "key": key,
                "name": name,
                "type": Platform.BINARY_SENSOR,
                "class": sens_class,
                "value": None,
            }
            sensor["value_fn"] = lambda s=sensor: binary_sensor_value(s)
            LOGGER.debug(f"[BINARY_SENSOR][{key}] {sensor}")
            return sensor
        if input_type in ["INT", "FLOAT", "STRING"]:
            meas_unit = measurement_unit(resource.get("measUnit"))
            sens_class = sensor_class(resource.get("measUnit"))
            sensor = {
                "id": resource["code"],
                "key": key,
                "name": name,
                "type": Platform.SENSOR,
                "class": sens_class,
                "state": state_class(sens_class),
                "unit": meas_unit,
                "value": None,
            }
            sensor["value_fn"] = lambda s=sensor: sensor_value(s)
            LOGGER.debug(f"[SENSOR][{key}] {sensor}")
            return sensor
        LOGGER.error(f"Unsupported input type {input_type} for {key}")
        return None

    @staticmethod
    def parse_value(value, code):
        """Parse an EmmeTI Febos resource value."""
        if isinstance(value, str):
            return value.strip()
        if code in ["R9120"]:
            return float(value) * 60.0
        if code in [
            "R8702",
            "R8703",
            "R8678",
            "R8680",
            "R8986",
            "R8987",
            "R8988",
            "R16444",
            "R16446",
            "R16448",
            "R16450",
            "R16451",
            "R16453",
            "R16455",
            "R16457",
            "R8989",
            "R8698",
            "setTemp",
            "temp",
        ]:
            return float(value) / 10.0
        if code in ["R8684", "R8686", "R8688", "R8690"]:
            return float(value) / 100.0
        if code in ["R8220", "R8221", "R8222", "R8223"]:
            return float(value) / 1000.0
        return value
