"""Sensor platform for Gecko."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from geckolib import GeckoErrorSensor, GeckoReminderType
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ICON
from .entity import GeckoEntity, GeckoEntityBase
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    sensors: list = []
    if spaman.status_sensor is not None:
        sensors.append(
            GeckoSensor(spaman, entry, spaman.status_sensor, EntityCategory.DIAGNOSTIC)
        )
    if spaman.show_ping_sensor and spaman.ping_sensor is not None:
        sensors.append(
            GeckoSensor(spaman, entry, spaman.ping_sensor, EntityCategory.DIAGNOSTIC)
        )
    if spaman.radio_sensor is not None:
        sensors.append(
            GeckoSensor(spaman, entry, spaman.radio_sensor, EntityCategory.DIAGNOSTIC)
        )
    if spaman.channel_sensor is not None:
        sensors.append(
            GeckoSensor(spaman, entry, spaman.channel_sensor, EntityCategory.DIAGNOSTIC)
        )
    if spaman.can_use_facade and spaman.facade is not None:
        for sensor in spaman.facade.sensors:
            sensors.append(GeckoSensor(spaman, entry, sensor))
        for reminder in spaman.facade.reminders_manager.reminders:
            sensors.append(GeckoReminderSensor(spaman, entry, reminder.type))
        sensors.append(GeckoErrorTextSensor(spaman, entry, spaman.facade.error_sensor))
    async_add_entities(sensors)


class GeckoSensor(GeckoEntity, SensorEntity):
    """Gecko Sensor class."""

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        return self._automation_entity.state

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._automation_entity.unit_of_measurement

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
        if type == GeckoReminderType.CLEAN_FILTER:
            return "Clean filter"
        if type == GeckoReminderType.CHANGE_WATER:
            return "Change water"
        if type == GeckoReminderType.CHECK_SPA:
            return "Check Spa"
        if type == GeckoReminderType.CHANGE_OZONATOR:
            return "Change Ozonator"
        if type == GeckoReminderType.CHANGE_VISION_CARTRIDGE:
            return "Change Vision cartridge"
        return "Unknown"


class GeckoErrorTextSensor(GeckoEntityBase, SensorEntity):
    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        error_sensor: GeckoErrorSensor,
    ) -> None:
        super().__init__(
            spaman,
            config_entry,
            f"{spaman.unique_id}-ERR",
            "Error(s)",
            spaman.spa_name,
        )
        self._error_sensor = error_sensor
        self._entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        if self.spaman.facade is None:
            return None
        return self._error_sensor.state

    @property
    def native_unit_of_measurement(self):
        return None

    @property
    def icon(self) -> str:
        return "mdi:alert"
