import voluptuous as vol
import lib8relay
import logging

from homeassistant.const import (
	CONF_NAME, CONF_PORT)

from homeassistant.components.light import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import SwitchEntity

CONF_RELAY="relay"
CONF_STACK="stack"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
	vol.Required(CONF_RELAY): cv.string,
	vol.Optional(CONF_PORT, default='0x3F'): cv.string,
	vol.Optional(CONF_NAME, default='relay8'): cv.string,
	vol.Optional(CONF_STACK, default=0): cv.string,
})

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
	"""Setup the 8relay platform."""
	add_devices([EigthRelay(
		port=config.get(CONF_PORT),
		name=config.get(CONF_NAME),
        stack=config.get(CONF_STACK),
        relay=config.get(CONF_RELAY)
	)])

class EigthRelay(SwitchEntity):
    """Sequent Microsystems Relay"""
    def __init__(self, port, name, stack, relay):
        self._port = int(port, 16)
        self._name = name
        self._relay = int(relay)
        self._stack = int(stack)

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        try:
            if lib8relay.get(self._stack, self._relay) == 0:
                return False
            else:
                return True
        except Exception as ex:
            _LOGGER.error("Is ON check failed, %e", ex)
            return False

    def turn_on(self, **kwargs):
        """Turn the device on."""
        try:
            lib8relay.set(self._stack, self._relay, 1)
        except Exception as ex:
            _LOGGER.error("Turn ON failed, %e", ex)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        try:
            lib8relay.set(self._stack, self._relay, 0)
        except Exception as ex:
            _LOGGER.error("Turn OFF failed, %e", ex)

