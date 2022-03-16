"""Sensor platform for Gecko."""
from datetime import datetime, timezone, timedelta
from geckolib import GeckoReminderType
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, ICON
from .entity import GeckoEntity, GeckoEntityBase
from .spa_manager import GeckoSpaManager


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    sensors = []
    if spaman.status_sensor is not None:
        sensors.append(GeckoSensor(spaman, entry, spaman.status_sensor))
    if spaman.ping_sensor is not None:
        sensors.append(GeckoSensor(spaman, entry, spaman.ping_sensor))
    if spaman.can_use_facade:
        for sensor in spaman.facade.sensors:
            sensors.append(GeckoSensor(spaman, entry, sensor))
        for reminder in spaman.facade.reminders_manager.reminders:
            sensors.append(GeckoReminderSensor(spaman, entry, reminder.type))
    async_add_entities(sensors)


class GeckoSensor(GeckoEntity, SensorEntity):
    """Gecko Sensor class."""

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self._automation_entity.state

    @property
    def native_unit_of_measurement(self):
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


class GeckoReminderSensor(GeckoEntityBase, SensorEntity):
    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        reminder_type: GeckoReminderType,
    ) -> None:
        super().__init__(
            spaman,
            config_entry,
            f"{spaman.unique_id}-{GeckoReminderType.to_string(reminder_type)}",
            f"{GeckoReminderSensor.type_to_name(reminder_type)} due",
            spaman.spa_name,
        )
        self._reminder_type = reminder_type

    @property
    def native_value(self):
        if self.spaman.facade is None:
            return None
        reminder = self.spaman.facade.reminders_manager.get_reminder(
            self._reminder_type
        )
        if reminder is None:
            return None
        today = datetime.utcnow().date()
        midnight = datetime(
            today.year, today.month, today.day, 0, 0, 0, 0, timezone.utc
        )
        return midnight + timedelta(reminder.days)

    @property
    def native_unit_of_measurement(self):
        return None

    @property
    def device_class(self) -> str:
        return "timestamp"

    @property
    def icon(self) -> str:
        return "mdi:reminder"

    @staticmethod
    def type_to_name(type: GeckoReminderType) -> str:
        # This should go via strings.json at some point
        if type == GeckoReminderType.RINSE_FILTER:
            return "Rinse filter"
        elif type == GeckoReminderType.CLEAN_FILTER:
            return "Clean filter"
        elif type == GeckoReminderType.CHANGE_WATER:
            return "Change water"
        elif type == GeckoReminderType.CHECK_SPA:
            return "Check Spa"
        elif type == GeckoReminderType.CHANGE_OZONATOR:
            return "Change Ozonator"
        elif type == GeckoReminderType.CHANGE_VISION_CARTRIDGE:
            return "Change Vision cartridge"
        else:
            return "Unknown"
