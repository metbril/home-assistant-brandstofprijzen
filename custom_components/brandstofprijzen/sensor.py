"""Brandstofprijzen Sensors."""

import logging
from datetime import datetime, timedelta

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_ICON,
    CONF_MONITORED_VARIABLES,
    CONF_NAME,
    CONF_PREFIX,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_OF_MEASUREMENT,
)
from homeassistant.util import Throttle

REQUIREMENTS = ["beautifulsoup4==4.13.4"]

_LOGGER = logging.getLogger(__name__)
_RESOURCE = "https://www.unitedconsumers.com/tanken/brandstofprijzen"

_USERAGENT = "UnitedConsumers Brandstofprijzen for Home Assistant"

ATTRIBUTION = "Data provided by UnitedConsumers"
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

class BrandstofprijzenSensor(SensorEntity):
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
    def state_class(self):
        """Return the state class."""
        return "measurement"

    @property
    def extra_state_attributes(self):
        return {ATTR_ATTRIBUTION: ATTRIBUTION}

    @property
    def available(self):
        return self.rest.available

    def update(self):
        self.rest.update()
        for idx, stype in enumerate(SENSOR_TYPES):
            if self.type == stype:
                try:
                    self._state = self.rest.data[idx]
                    _LOGGER.debug("Updated sensor %s to %.3f", self.type, self._state)
                except (TypeError, IndexError):
                    self._state = None

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

            price_elements = soup.select('span[data-sentry-component="Price"]')

            data = []
            for idx, el in enumerate(price_elements):
                text = el.get_text(strip=True)
                if "€" in text:
                    try:
                        value = float(text.replace("€", "").replace(",", ".").strip())
                        data.append(value)
                    except ValueError:
                        _LOGGER.warning(f"Kon geen getal maken van prijs: {text}")
                else:
                    _LOGGER.warning(f"[{idx}] Geen euro-teken in tekst: '{text}'")

            self.data = data
            self.available = True
            _LOGGER.debug(f"Geparsed prijzen: {data}")
        except requests.exceptions.ConnectionError:
            _LOGGER.error("Connection error")
            self.data = None
            self.available = False
