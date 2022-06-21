"""Platform for light integration."""
from __future__ import annotations

import logging
import requests
from math import floor
from custom_components.homewizard_custom.lib.rest import HomeWizardREST
import voluptuous as vol

from pprint import pformat
# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    LightEntity,
    SUPPORT_BRIGHTNESS
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the HomeWizard Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]
    password = config.get(CONF_PASSWORD)

    # do stuff here
    sensors = requests.get(f'http://{host}/{password}/get-sensors').json()
    switches: list = sensors['response']["switches"]

    dimmers = list()
    for switch in switches:
        if switch['type'] == "dimmer":
            dimmers.append(
                HomeWizardDimmer(HomeWizardREST(host, password), switch['id'], switch['name'])
            )

    add_entities(dimmers)

    # Setup connection with devices/cloud

class HomeWizardDimmer(LightEntity):
    """Representation of an HomeWizard light."""

    def __init__(self, client: HomeWizardREST, id, name) -> None:
        """Initialize an AwesomeLight."""
        self._hwid = id
        self._client = client
        self._name = name
        self._state = None
        self._brightness = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.
        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS

    @property
    def unique_id(self):
        return f'homewizard_{self._hwid}'

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
            self._client.set_dimmer(self._hwid, floor(brightness / 2.55))
            return

        self._client.turn_switch(self._hwid, "on")

    def turn_off(self, **kwargs: Any) -> None:
        self._client.turn_switch(self._hwid, "off")

    def update(self) -> None:
        """Fetch new state data for this light.
        This is the only method that should fetch new data for Home Assistant.
        """
        switch = self._client.get_switch(self._hwid)
        if switch == None:
            return
        self._state = True if switch['status'] == "on" else False
        self._brightness = floor(switch['dimlevel'] * 2.55)