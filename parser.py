"""EmmeTI Febos helpers for Home Assistant integration."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from febos.api import FebosApi, Input, Slave
from febos.errors import AuthenticationError
from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    CURRENCY_EURO,
    PERCENTAGE,
    Platform,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)

from .const import DOMAIN, LOGGER

MISSING_MEASUREMENT_UNIT_MAP = {
    "CT_UPTIME": "",  # Uptime
    "CT_VPN_IP": "",  # OpenVPN IP Address
    "R16493": "",  # Orario della prima richiesta ACS
    "R16494": "°C",  # Set temp. della prima richiesta ACS
    "R16495": "°C",  # Set temp. della seconda richiesta ACS
    "R16496": "°C",  # Set temp. della seconda richiesta ACS
    "R16497": "°C",  # Set temp. di mantenimento ACS
    "R16515": "",  # Set di Rugiada/Umidita
    "R8200": "",  # Superparametro 1
    "R8201": "",  # Superparametro 2
    "R8202": "",  # Superparametro 3
    "R8203": "",  # Offset sonda NTC1
    "R8204": "",  # Offset sonda NTC2
    "R8205": "",  # not used
    "R8206": "",  # not used
    "R8207": "",  # not used
    "R8208": "",  # Minima durata impulso contatore HP
    "R8209": "",  # Massima durata impulso contatore HP
    "R8210": "",  # Valore corrispondente ad 1 impulso
    "R8211": "",  # Minima durata impulso contatore Presa
    "R8212": "",  # Massima durata impulso contatore Presa
    "R8213": "",  # Valore corrispondente ad 1 impulso
    "R8214": "",  # Minima durata impulso contatore FV
    "R8215": "",  # Massima durata impulso contatore FV
    "R8216": "",  # Valore corrispondente ad 1 impulso
    "R8217": "",  # Minima durata impulso contatore Casa
    "R8218": "",  # Massima durata impulso contatore Casa
    "R8219": "",  # Valore corrispondente ad 1 impulso
    "R8300": "",  # N. impulsi scartati perchè corti FV
    "R8301": "",  # N. impulsi scartati perchè lunghi FV
    "R8302": "",  # N. impulsi scartati perchè troppo vicini FV
    "R8303": "",  # N. impulsi scartati perchè corti CASA
    "R8304": "",  # N. impulsi scartati perchè lunghi CASA
    "R8305": "",  # N. impulsi scartati perchè troppo vicini CASA
    "R8306": "",  # N. impulsi scartati perchè corti HP
    "R8307": "",  # N. impulsi scartati perchè lunghi HP
    "R8308": "",  # N. impulsi scartati perchè troppo vicini HP
    "R8309": "",  # N. impulsi scartati perchè corti PRESA
    "R8310": "",  # N. impulsi scartati perchè lunghi PRESA
    "R8311": "",  # N. impulsi scartati perchè troppo vicini PRESA
    "R8400": "",  # Calibrazione tensione CH1
    "R8401": "",  # Calibrazione corrente CH1
    "R8402": "",  # Calibrazione corrente CH2
    "R8403": "",  # Offset potenza attiva CH1
    "R8404": "",  # Offset potenza attiva CH2
    "R8405": "",  # Compensazione fase tensione CH1
    "R8406": "",  # Compensazione fase corrente CH1
    "R8407": "",  # Compensazione fase corrente CH2
    "R8408": "",  # Contenuto del registro di taratura della tensione CH1
    "R8409": "",  # Contenuto del registro di taratura della corrente CH1 (Word più significativa)
    "R8410": "",  # Contenuto del registro di taratura della corrente CH1 (Word meno significativa)
    "R8411": "",  # Contenuto del registro di taratura della corrente CH2 (Word più significativa)
    "R8412": "",  # Contenuto del registro di taratura della corrente CH2 (Word meno significativa)
    "R8413": "",  # Contenuto del registro di taratura dello sfasamento relativo a CH1
    "R8414": "",  # Contenuto del registro di taratura dello sfasamento relativo a CH2
    "R8600": "",  # Data produzione (parte alta)
    "R8638": "",  # Configurazione potenze 1
    "R8639": "",  # Configurazione potenze 2
    "R8640": "",  # Configurazione potenze 3
    "R8641": "",  # Configurazione potenze 4
    "R8642": "",  # Configurazione potenze 5
    "R8648": "",  # Stagione
    "R8660": "%",  # Set umidità estate (SetRh_E)
    "R8661": "%",  # Set umidità inverno (SetRh_I)
    "R8664": "",  # Nome Febos Crono
    "R8665": "kW",  # Massima potenza fornita
    "R8666": "kW",  # Potenza FV installata
    "R8756": "kW",  # Potenza prelevata dalla rete
    "R8757": "kW",  # Potenza immessa in rete
    "R8758": "kW",  # Potenza_Home
    "R8759": "kW",  # Potenza_FV
    "R8760": "kW",  # Potenza_PDC
    "R8761": "kW",  # Potenza_Acs
    "R8762": "kW",  # Potenza_Presa1
    "R8763": "kW",  # Potenza_Risc_Pdc
    "R8764": "kW",  # Potenza_Raff_Pdc
    "R8765": "watt/h",  # Energia prelevata dalla rete
    "R8766": "watt/h",  # Energia immessa in rete
    "R8767": "watt/h",  # Energia_Home
    "R8768": "watt/h",  # Energia_FV
    "R8769": "watt/h",  # Energia_PdC
    "R8770": "watt/h",  # Energia_ACS
    "R8771": "watt/h",  # Energia_Presa
    "R8772": "watt/h",  # Energia_Risc_Pdc
    "R8773": "watt/h",  # Energia_Raff_Pdc
    "R8774": "",  # EER/COP
    "R8967": "",  # Sbrinamento
    "R9008": "",  # Step frequenza PdC
    "R9042": "°C",  # Temperatura minima acqua Radiante
    "R9051": "°C",  # Temperatura attuale Acqua PdC
    "R9052": "°C",  # Set temperatura Acqua PdC
    "R9071": "",  # Riscaldamento Add.
    "R9072": "",  # Valvola 3 Vie
    "R9076": "",  # Fotovoltaico
    "R9078": "",  # Antigelo
    "R9079": "",  # Antigelo_2
}

MEASUREMENT_UNIT_MAP = {
    "kW": UnitOfPower.KILO_WATT,
    "°C": UnitOfTemperature.CELSIUS,
    "°": UnitOfTemperature.CELSIUS,
    "h": UnitOfTime.HOURS,
    "HH:mm": UnitOfTime.MINUTES,
    "watt/h": UnitOfEnergy.WATT_HOUR,
    "L/h": UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
    "e/kw": CURRENCY_EURO,
    "%": PERCENTAGE,
    "": None,
}

SENSOR_DEVICE_CLASS_MAP = {
    UnitOfPower: SensorDeviceClass.POWER,
    UnitOfTemperature: SensorDeviceClass.TEMPERATURE,
    UnitOfTime: SensorDeviceClass.DURATION,
    UnitOfEnergy: SensorDeviceClass.ENERGY,
    UnitOfVolumeFlowRate: SensorDeviceClass.VOLUME_FLOW_RATE,
    None: SensorDeviceClass.ENUM,
}

SENSOR_STATE_CLASS_MAP = {
    SensorDeviceClass.MONETARY: SensorStateClass.TOTAL,
    SensorDeviceClass.POWER: SensorStateClass.MEASUREMENT,
    SensorDeviceClass.TEMPERATURE: SensorStateClass.MEASUREMENT,
    SensorDeviceClass.DURATION: SensorStateClass.MEASUREMENT,
    SensorDeviceClass.ENERGY: SensorStateClass.TOTAL,
    SensorDeviceClass.VOLUME_FLOW_RATE: SensorStateClass.MEASUREMENT,
    SensorDeviceClass.HUMIDITY: SensorStateClass.MEASUREMENT,
    SensorDeviceClass.ENUM: SensorStateClass.MEASUREMENT,
}

BINARY_SENSOR_DEVICE_CLASS_MAP = {
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
}

INPUT_TYPE_MAP = {
    "INT": int,
    "FLOAT": float,
    "BOOL": bool,
    "STRING": str,
}

SENSOR_VALUE_MAP = {
    None: lambda v: None,
    "R9120": lambda v: float(v) * 60.0,
    "R8702": lambda v: float(v) / 10.0,
    "R8703": lambda v: float(v) / 10.0,
    "R8678": lambda v: float(v) / 10.0,
    "R8680": lambda v: float(v) / 10.0,
    "R8986": lambda v: float(v) / 10.0,
    "R8987": lambda v: float(v) / 10.0,
    "R8988": lambda v: float(v) / 10.0,
    "R16444": lambda v: float(v) / 10.0,
    "R16446": lambda v: float(v) / 10.0,
    "R16448": lambda v: float(v) / 10.0,
    "R16450": lambda v: float(v) / 10.0,
    "R16451": lambda v: float(v) / 10.0,
    "R16453": lambda v: float(v) / 10.0,
    "R16455": lambda v: float(v) / 10.0,
    "R16457": lambda v: float(v) / 10.0,
    "R8989": lambda v: float(v) / 10.0,
    "R8698": lambda v: float(v) / 10.0,
    "setTemp": lambda v: float(v) / 10.0,
    "temp": lambda v: float(v) / 10.0,
    "R8684": lambda v: float(v) / 100.0,
    "R8686": lambda v: float(v) / 100.0,
    "R8688": lambda v: float(v) / 100.0,
    "R8690": lambda v: float(v) / 100.0,
    "R8220": lambda v: float(v) / 1000.0,
    "R8221": lambda v: float(v) / 1000.0,
    "R8222": lambda v: float(v) / 1000.0,
    "R8223": lambda v: float(v) / 1000.0,
}

BINARY_SENSOR_VALUE_MAP = {
    None: lambda v: None,
    BinarySensorDeviceClass.COLD: lambda v: not bool(v),
    BinarySensorDeviceClass.PRESENCE: lambda v: not bool(v),
    BinarySensorDeviceClass.PROBLEM: bool,
    BinarySensorDeviceClass.RUNNING: bool,
    BinarySensorDeviceClass.RUNNING: bool,
    BinarySensorDeviceClass.RUNNING: bool,
    BinarySensorDeviceClass.RUNNING: bool,
    BinarySensorDeviceClass.RUNNING: bool,
    BinarySensorDeviceClass.RUNNING: bool,
    BinarySensorDeviceClass.RUNNING: bool,
    BinarySensorDeviceClass.WINDOW: bool,
}


@dataclass
class FebosResourceData:
    """Parsed EmmeTI Febos resource."""

    id: str
    name: str
    type: Platform
    sensor_class: BinarySensorDeviceClass | SensorDeviceClass
    key: str
    value_type: type
    state_class: SensorStateClass = None
    meas_unit: str = None
    value: Any = None

    def set_value(self, value: Any) -> None:
        """Set current value."""
        self.value = self.value_type(value)

    def get_value(self) -> Any:
        """Return current value."""
        if self.type == Platform.SENSOR:
            return SENSOR_VALUE_MAP.get(self.id, lambda v: v)(self.value)
        if self.type == Platform.BINARY_SENSOR:
            return BINARY_SENSOR_VALUE_MAP[self.sensor_class](self.value)
        raise ValueError(self.type)

    def _parse_binary_sensor_value(self):
        """Normalize the binary sensor value."""
        if self.value is None:
            return None
        if self.sensor_class in [
            BinarySensorDeviceClass.COLD,
            BinarySensorDeviceClass.PRESENCE,
        ]:
            return not bool(self.value)
        return bool(self.value)

    @staticmethod
    def parse(resource: Input, installation_id: int):
        """Parse an EmmeTI Febos resource."""

        def normalize_name(n):
            n = n.replace(" (in KW)", "")
            return n if len(n) > 0 else "Unknown"

        def normalize_sensor_class(u):
            if u == PERCENTAGE:
                return SensorDeviceClass.HUMIDITY
            if u == CURRENCY_EURO:
                return SensorDeviceClass.MONETARY
            return SENSOR_DEVICE_CLASS_MAP.get(type(u), SensorDeviceClass.ENUM)

        def normalize_measurement_unit(r):
            if r.measUnit is None and r.code not in MISSING_MEASUREMENT_UNIT_MAP:
                LOGGER.warning(f"{r.code}: {r.name}")
            return MISSING_MEASUREMENT_UNIT_MAP.get(r.code, "")

        key = f"{DOMAIN}_{installation_id}_{resource.deviceId}_{resource.thingId}_{resource.code.lower()}"
        name = normalize_name(resource.label)
        value_type = INPUT_TYPE_MAP[resource.inputType]
        if value_type is bool:
            bscls = BINARY_SENSOR_DEVICE_CLASS_MAP.get(resource.code)
            if bscls is None:
                return None
            return FebosResourceData(
                id=resource.code,
                key=key,
                name=name,
                type=Platform.BINARY_SENSOR,
                sensor_class=bscls,
                value_type=value_type,
            )
        if value_type in [int, float, str]:
            if not hasattr(resource, "measUnit"):
                return None
            unit = normalize_measurement_unit(resource)
            scls = normalize_sensor_class(unit)
            if scls is None:
                return None
            return FebosResourceData(
                id=resource.code,
                key=key,
                name=name,
                type=Platform.SENSOR,
                sensor_class=scls,
                state_class=SENSOR_STATE_CLASS_MAP[scls],
                meas_unit=unit,
                value_type=value_type,
            )
        raise ValueError(resource)


SLAVE_RESOURCES = {
    "callTemp": FebosResourceData(
        id="S01",
        name="Chiamata Temperatura",
        type=Platform.BINARY_SENSOR,
        sensor_class=BinarySensorDeviceClass.HEAT,
        key=None,
        value_type=bool,
    ),
    "callHumid": FebosResourceData(
        id="S02",
        name="Chiamata Umidità",
        type=Platform.BINARY_SENSOR,
        sensor_class=BinarySensorDeviceClass.HEAT,
        key=None,
        value_type=bool,
    ),
    "stagione": FebosResourceData(
        id="S03",
        name="Stagione",
        type=Platform.BINARY_SENSOR,
        sensor_class=BinarySensorDeviceClass.COLD,
        key=None,
        value_type=bool,
    ),
    "setTemp": FebosResourceData(
        id="S04",
        name="Set Temperatura",
        type=Platform.SENSOR,
        sensor_class=SensorDeviceClass.TEMPERATURE,
        key=None,
        value_type=float,
    ),
    "temp": FebosResourceData(
        id="S05",
        name="Temperatura",
        type=Platform.SENSOR,
        sensor_class=SensorDeviceClass.TEMPERATURE,
        key=None,
        value_type=float,
    ),
    "humid": FebosResourceData(
        id="S06",
        name="Umidità",
        type=Platform.SENSOR,
        sensor_class=SensorDeviceClass.HUMIDITY,
        key=None,
        value_type=float,
    ),
    "confort": FebosResourceData(
        id="S07",
        name="Comfort",
        type=Platform.BINARY_SENSOR,
        sensor_class=BinarySensorDeviceClass.PRESENCE,
        key=None,
        value_type=bool,
    ),
}


@dataclass
class FebosSlaveData:
    """Parsed EmmeTI Febos slave."""

    id: str
    name: str
    resources: dict[str, FebosResourceData]

    def _create_resource(self, name: str, device: FebosDeviceData) -> FebosResourceData:
        resource = copy.deepcopy(SLAVE_RESOURCES[name])
        resource.key = (
            f"{DOMAIN}_{device.installation_id}_{device.id}_{self.id}_{name.lower()}"
        )
        return resource

    @staticmethod
    def parse(slave: Slave, device: FebosDeviceData) -> FebosSlaveData:
        """Parse an EmmeTI Febos slave."""
        slv = FebosSlaveData(
            id=slave.indirizzoSlave,
            name=f"{device.model} Slave {slave.indirizzoSlave}",
            resources={},
        )
        slv.resources = {
            k: slv._create_resource(k, device)
            for k in slave.__dict__
            if k in SLAVE_RESOURCES
        }
        return slv


@dataclass
class FebosThingData:
    """Parsed EmmeTI Febos device."""

    id: int
    name: str
    resources: dict[str, FebosResourceData]


@dataclass
class FebosDeviceData:
    """Parsed EmmeTI Febos device."""

    id: int
    installation_id: int
    manufacturer: str
    model: str
    name: str
    slaves: dict[str, FebosSlaveData]
    things: dict[str, FebosThingData]


@dataclass
class FebosInstallationData:
    """Parsed EmmeTI Febos installation."""

    id: int
    devices: dict[str, FebosDeviceData]
    groups: set[str]


@dataclass
class FebosClient:
    """EmmeTI Febos client."""

    def __init__(self, api: FebosApi) -> None:
        """Initialize a client."""
        self.api = api
        self.resources = []

    def get_resources(self) -> list[FebosInstallationData]:
        """Return a list of installations with their devices, things, slaves and resources."""
        data = []
        login = self.api.login()
        LOGGER.debug("Logged in")
        for installation_id in login.installationIdList:
            installation = FebosInstallationData(
                id=installation_id, devices={}, groups=set()
            )
            data.append(installation)
            response = self.api.page_config(installation.id)
            for device in response.deviceMap.values():
                device = FebosDeviceData(
                    id=device.id,
                    installation_id=device.installationId,
                    manufacturer=device.tenantName,
                    model=device.modelName,
                    name=f"{device.tenantName} {device.modelName} {device.deviceTypeName.capitalize()}",
                    slaves={},
                    things={},
                )
                installation.devices[device.id] = device
                response2 = self.api.get_febos_slave(installation.id, device.id)
                for slave in response2:
                    slave = FebosSlaveData.parse(slave, device)
                    device.slaves[slave.id] = slave
            for thing in response.thingMap.values():
                device = installation.devices[thing.deviceId]
                device.things[thing.id] = FebosThingData(
                    id=thing.id, name=thing.modelName, resources={}
                )
            for page in response.pageMap.values():
                for tab in page.tabList:
                    for widget in tab.widgetList:
                        for group in widget.widgetInputGroupList:
                            installation.groups.add(group.inputGroupGetCode)
                            thing = installation.devices[group.deviceId].things[
                                group.thingId
                            ]
                            for resource in group.inputList:
                                resource = FebosResourceData.parse(
                                    resource, installation.id
                                )
                                if resource is not None:
                                    thing.resources[resource.id] = resource
        self.resources = data
        LOGGER.debug("Resources loaded")
        return self.resources

    def _update(self):
        """Get an updated value for all resources."""
        for installation in self.resources:
            response = self.api.realtime_data(installation.id, installation.groups)
            for entry in response:
                thing = installation.devices[entry.deviceId].things[entry.thingId]
                for code, value in entry.data.items():
                    if code in thing.resources:
                        thing.resources[code].set_value(value.i)
            for device in installation.devices.values():
                response = self.api.get_febos_slave(installation.id, device.id)
                for slave in response:
                    for code, value in slave.__dict__.items():
                        resources = device.slaves[slave.indirizzoSlave].resources
                        if code in resources:
                            resources[code].set_value(value)

    def update_values(self):
        """Get an updated value for all resources. Retry login in case of session timeout."""
        try:
            self._update()
            LOGGER.debug("Values updated")
        except AuthenticationError as e:
            LOGGER.debug("Session timed out")
            LOGGER.debug(str(e))
            self.api.login()
            LOGGER.debug("Logged in")
            self._update()
