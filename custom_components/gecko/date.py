"""Date platform for Gecko."""

import logging
from datetime import UTC, date, datetime, timedelta
from typing import Any

from geckolib import GeckoReminderType
from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATE, DOMAIN
from .entity import GeckoEntity, GeckoEntityBase
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up date platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    dates: list = []
    if (
        spaman.can_use_facade
        and spaman.facade is not None
        and spaman.facade.reminders_manager.is_available
    ):
        dates.extend(
            GeckoReminderDate(spaman, entry, reminder.reminder_type)
            for reminder in spaman.facade.reminders_manager.reminders
        )
    async_add_entities(dates)
    spaman.platform_loaded(DATE)


class GeckoDate(GeckoEntity, DateEntity):
    """Gecko Date class."""

    @property
    def native_value(self) -> Any:
        """Return the native value of the sensor."""
        return self._automation_entity.state

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._automation_entity.unit_of_measurement

    @property
    def device_class(self) -> str:
        """Return the device class of the sensor."""
        return self._automation_entity.device_class


class GeckoReminderDate(GeckoEntityBase, DateEntity):
    """Gecko reminder sensor class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        reminder_type: GeckoReminderType,
    ) -> None:
        """Initialize the reminder sensor."""
        super().__init__(
            spaman,
            config_entry,
            f"{spaman.unique_id}-{GeckoReminderType.to_string(reminder_type)}",
            f"{GeckoReminderDate.type_to_name(reminder_type)} due",
            spaman.spa_name,
        )
        self._reminder_type = reminder_type
        self.spaman.facade.reminders_manager.watch(self._on_change)
        self._entity_category = EntityCategory.CONFIG

    @property
    def native_value(self) -> datetime | None:
        """Get the sensor native value."""
        if self.spaman.facade is None:
            return None
        reminder = self.spaman.facade.reminders_manager.get_reminder(
            self._reminder_type
        )
        if reminder is None:
            return None
        today = datetime.now(tz=UTC).date()
        midnight = datetime(today.year, today.month, today.day, 0, 0, 0, 0, UTC)
        return midnight + timedelta(reminder.days)

    async def async_set_value(self, value: date) -> None:
        """Update the current value."""
        if self.spaman.facade is None:
            return
        today = datetime.now(tz=UTC).date()
        delta = value - today
        _LOGGER.debug("Set reminder delta to %d", delta.days)
        await self.spaman.facade.reminders_manager.set_reminder(
            self._reminder_type, delta.days
        )

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Get native unit of measurement."""
        return None

    @property
    def device_class(self) -> str:
        """Get device class."""
        return "timestamp"

    @property
    def icon(self) -> str:
        """Get icon."""
        return "mdi:reminder"

    @staticmethod
    def type_to_name(thetype: GeckoReminderType) -> str:  # noqa: PLR0911
        """Convert type to name."""
        # This should go via strings.json at some point
        if thetype == GeckoReminderType.RINSE_FILTER:
            return "Rinse filter"
        if thetype == GeckoReminderType.CLEAN_FILTER:
            return "Clean filter"
        if thetype == GeckoReminderType.CHANGE_WATER:
            return "Change water"
        if thetype == GeckoReminderType.CHECK_SPA:
            return "Check Spa"
        if thetype == GeckoReminderType.CHANGE_OZONATOR:
            return "Change Ozonator"
        if thetype == GeckoReminderType.CHANGE_VISION_CARTRIDGE:
            return "Change Vision cartridge"
        return "Unknown"

    def _on_change(self, _sender: Any, _old_value: Any, _new_value: Any) -> None:
        """Notify HA of the change."""
        if self.hass is not None:
            self.async_schedule_update_ha_state(force_refresh=True)
