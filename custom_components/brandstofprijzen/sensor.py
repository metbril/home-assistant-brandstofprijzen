"""Brandstofprijzen Sensors."""

import logging
from datetime import datetime, timedelta

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_ICON,
    CONF_PREFIX,
    CONF_NAME,
    CONF_MONITORED_VARIABLES,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ["beautifulsoup4==4.9.3"]

_LOGGER = logging.getLogger(__name__)
_RESOURCE = "https://www.unitedconsumers.com/brandstofprijzen/"

# List: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
_USERAGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"

ATTRIBUTION = "Data provided by United Consumers"
DEFAULT_ICON = "mdi:gas-station"
DEFAULT_PREFIX = "Adviesprijs"
DEFAULT_UNIT_OF_MEASUREMENT = "€/L"

# Prevent hammering the webpage, prices usually change once a day
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
# Prevent fetching the page again for each sensor
MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=1)

# All fuel types on the page, in page order.
SENSOR_TYPES = {
    "euro95": ["Euro95"],
    "diesel": ["Diesel"],
    "lpg": ["LPG"],
    "super": ["Super"],
    "super_mlv": ["Super MLV"],
    "premium_benzines": ["Premium benzines"],
    "premium_diesels": ["Premium diesels"],
    "blueone95": ["BlueOne95"],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_MONITORED_VARIABLES, default=list(SENSOR_TYPES)): vol.All(
            cv.ensure_list, [vol.In(SENSOR_TYPES)]
        ),
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
        vol.Optional(
            CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT
        ): cv.string,
        vol.Optional(CONF_PREFIX, default=DEFAULT_PREFIX): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    }
)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Brandstofprijzen sensor."""
    scan_interval = config[CONF_SCAN_INTERVAL]
    rest = BrandstofprijzenData(_RESOURCE)
    if config[CONF_MONITORED_VARIABLES] == []:
        config[CONF_MONITORED_VARIABLES] = SENSOR_TYPES
    variables = []
    for variable in config[CONF_MONITORED_VARIABLES]:
        variables.append(BrandstofprijzenSensor(variable, rest, config))
    add_devices(variables, True)


class BrandstofprijzenSensor(Entity):
    """Implementing the Brandstofprijzen sensor."""

    def __init__(self, sensor_type, rest, config):
        """Initialize the sensor."""
        self._name = config[CONF_PREFIX].rstrip() + " " + SENSOR_TYPES[sensor_type][0]
        self._unit_of_measurement = config[CONF_UNIT_OF_MEASUREMENT]
        self._icon = config[CONF_ICON]
        self.rest = rest
        self.type = sensor_type
        self._state = None

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    @property
    def state(self):
        """Return the state."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {}
        attr[ATTR_ATTRIBUTION] = ATTRIBUTION
        return attr

    @property
    def available(self):
        """Could the device be accessed during the last update call."""
        return self.rest.available

    def update(self):
        """Update current date."""
        self.rest.update()
        for idx, stype in enumerate(SENSOR_TYPES):
            if self.type == stype:
                try:
                    self._state = self.rest.data[idx]
                    _LOGGER.debug("Updated sensor %s to %.3f", self.type, self._state)
                except TypeError:
                    self._state = None
                    _LOGGER.error("Unable to update %s", self.type)


class BrandstofprijzenData(object):
    """Get data from site."""

    def __init__(self, sensor):
        """Initialize the data object."""
        self._sensor = sensor
        self.data = None
        self.available = True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data."""
        from bs4 import BeautifulSoup

        headers = {"User-Agent": _USERAGENT}
        try:
            r = requests.get(self._sensor, headers=headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            req_soup = soup.find("div", class_="table")
            soup_info = req_soup.find_all("div", class_="table-row")
            data = []
            for count, row in enumerate(soup_info):
                if count > 0:
                    data.append(
                        float(
                            row.select("div:nth-of-type(3)")[0]
                            .get_text()
                            .split()[1]
                            .replace(",", ".")
                        )
                    )
            self.data = data
            self.available = True
            _LOGGER.debug(data)
        except requests.exceptions.ConnectionError:
            _LOGGER.error("Connection error")
            self.data = None
            self.available = False
