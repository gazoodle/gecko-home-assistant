"""Number platform for Gecko."""

import logging
from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, NUMBER
from .entity import GeckoEntity

if TYPE_CHECKING:
    from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up number platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    numbers: list = []
    if spaman.can_use_facade and spaman.facade is not None:
        if spaman.facade.mrsteam.is_available:
            numbers.append(
                GeckoNumber(spaman, entry, spaman.facade.mrsteam.user_runtime, None)
            )
        if spaman.facade.bainultra.is_available:
            numbers.append(
                GeckoNumber(spaman, entry, spaman.facade.bainultra.bath_runtime, None)
            )
            numbers.append(
                GeckoNumber(spaman, entry, spaman.facade.bainultra.bath_intensity, None)
            )
            numbers.append(
                GeckoNumber(
                    spaman,
                    entry,
                    spaman.facade.bainultra.drying_cycle_delay,
                    EntityCategory.CONFIG,
                )
            )
            numbers.append(
                GeckoNumber(
                    spaman,
                    entry,
                    spaman.facade.bainultra.drying_cycle_hour,
                    EntityCategory.CONFIG,
                )
            )
            numbers.append(
                GeckoNumber(
                    spaman,
                    entry,
                    spaman.facade.bainultra.drying_cycle_minute,
                    EntityCategory.CONFIG,
                )
            )

    async_add_entities(numbers)
    spaman.platform_loaded(NUMBER)


class GeckoNumber(GeckoEntity, NumberEntity):
    """Gecko Date class."""

    @property
    def native_value(self) -> float:
        """Return the native value of the sensor."""
        return self._automation_entity.native_value

    @property
    def native_min_value(self) -> float:
        """Get the min value."""
        return self._automation_entity.native_min_value

    @property
    def native_max_value(self) -> float:
        """Get the max value."""
        return self._automation_entity.native_max_value

    async def async_set_native_value(self, new_value: float) -> None:
        """Set the value of the number entity."""
        await self._automation_entity.async_set_native_value(new_value)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._automation_entity.native_unit_of_measurement

    @property
    def native_step(self) -> float:
        """Retuurn the step size."""
        return self._automation_entity.native_step

    @property
    def mode(self) -> str:
        """Return the preferred entry mode."""
        return self._automation_entity.mode

    @property
    def device_class(self) -> str:
        """Return the device class of the sensor."""
        return ""  # self._automation_entity.device_class
