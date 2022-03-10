"""Sensor platform for Gecko."""
from datetime import date, datetime
from homeassistant.helpers.typing import StateType
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, ICON
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [GeckoSensor(entry, sensor) for sensor in spaman.facade.sensors],
        True,
    )


class GeckoSensor(GeckoEntity, SensorEntity):
    """Gecko Sensor class."""

    @property
    def native_value(self) -> StateType | date | datetime:
        """Return the native value of the sensor."""
        return self._automation_entity.state

    @property
    def native_unit_of_measurement(self) -> str | None:
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
