"""Sensor platform for Gecko."""
from .const import DOMAIN, ICON
from .entity import GeckoEntity


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    facade = hass.data[DOMAIN][entry.entry_id].facade
    async_add_entities(
        [GeckoSensor(entry, sensor) for sensor in facade.sensors],
        True,
    )


class GeckoSensor(GeckoEntity):
    """Gecko Sensor class."""

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._automation_entity.state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._automation_entity.unit_of_measurement

    @property
    def aicon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return self._automation_entity.device_class
