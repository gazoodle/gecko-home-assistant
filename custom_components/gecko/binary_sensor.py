"""Binary sensor platform for Gecko."""
from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .entity import GeckoEntity


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup binary_sensor platform."""
    facade = hass.data[DOMAIN][entry.entry_id].facade
    async_add_entities(
        [GeckoBinarySensor(entry, sensor) for sensor in facade.binary_sensors], True
    )


class GeckoBinarySensor(GeckoEntity, BinarySensorEntity):
    """gecko binary_sensor class."""

    def __init__(self, config_entry, automation_entity):
        super().__init__(config_entry, automation_entity)

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._automation_entity.is_on
