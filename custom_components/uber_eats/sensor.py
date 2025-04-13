"""
Uber Eats Order Tracker for Home Assistant.
For more details about this platform, please refer to the documentation at
https://github.com/f0rky/home-assistant-blueprints/uber-eats-tracker
"""
import logging
import re
import asyncio
import aiohttp
import async_timeout
import voluptuous as vol
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME,
    CONF_SCAN_INTERVAL,
)
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_TRACKING_URL = "tracking_url"

DEFAULT_NAME = "Uber Eats Order"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TRACKING_URL): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
})

STATUS_UNKNOWN = "unknown"
STATUS_PREPARING = "preparing"
STATUS_ON_THE_WAY = "on its way"
STATUS_NEARBY = "nearby"
STATUS_ARRIVED = "arrived"
STATUS_DELIVERED = "delivered"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Uber Eats sensor."""
    name = config.get(CONF_NAME)
    tracking_url = config.get(CONF_TRACKING_URL)
    
    async_add_entities([UberEatsSensor(name, tracking_url)], True)


class UberEatsSensor(Entity):
    """Implementation of the Uber Eats sensor."""

    def __init__(self, name, tracking_url):
        """Initialize the sensor."""
        self._name = name
        self._tracking_url = tracking_url
        self._state = STATUS_UNKNOWN
        self._attributes = {
            "eta": "unknown",
            "driver_name": "Your driver",
            "distance": "nearby",
            "tracking_url": tracking_url
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            async with aiohttp.ClientSession() as session:
                with async_timeout.timeout(30):
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    async with session.get(self._tracking_url, headers=headers) as response:
                        html = await response.text()
                        
                        # Parse the order status
                        if "Preparing your order" in html:
                            self._state = STATUS_PREPARING
                        elif "On the way" in html:
                            self._state = STATUS_ON_THE_WAY
                        elif "nearby" in html or "minutes away" in html:
                            self._state = STATUS_NEARBY
                        elif "Arrived" in html or "at your door" in html:
                            self._state = STATUS_ARRIVED
                        elif "Delivered" in html or "Enjoy" in html:
                            self._state = STATUS_DELIVERED
                        
                        # Parse ETA
                        eta_match = re.search(r'(\d+)\s*min', html, re.IGNORECASE)
                        if eta_match:
                            self._attributes["eta"] = f"{eta_match.group(1)} minutes"
                        
                        # Parse driver name
                        driver_match = re.search(r'([A-Z][a-z]+)\s+is\s+(delivering|bringing)', html, re.IGNORECASE)
                        if driver_match:
                            self._attributes["driver_name"] = driver_match.group(1)
                        
                        # Parse distance
                        distance_match = re.search(r'(\d+(?:\.\d+)?)\s*(miles|km|mi)', html, re.IGNORECASE)
                        if distance_match:
                            self._attributes["distance"] = f"{distance_match.group(1)} {distance_match.group(2)} away"
                        
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Error fetching Uber Eats data: %s", err)
