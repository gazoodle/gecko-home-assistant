"""Water heater platform for Gecko."""

import logging
from typing import Any

from geckolib import GeckoAsyncFacade, GeckoWaterHeaterAbstract
from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ERROR_COUNT_TOLERANCE, WATER_HEATER
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up climate platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    if spaman.facade is not None:
        facade: GeckoAsyncFacade = spaman.facade
        water_heaters = []

        water_heaters.append(
            GeckoHAWaterHeater(
                spaman,
                entry,
                facade.water_heater,
            )
        )
        if spaman.facade.mrsteam.is_available:
            water_heaters.append(GeckoHAWaterHeater(spaman, entry, facade.mrsteam))

        async_add_entities(water_heaters)

    spaman.platform_loaded(WATER_HEATER)


class GeckoHAWaterHeater(GeckoEntity, WaterHeaterEntity):
    """Gecko Water Heater class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        automation_entity: GeckoWaterHeaterAbstract,
    ) -> None:
        """Initialize Gecko climate entity."""
        self._attr_supported_features = WaterHeaterEntityFeature.TARGET_TEMPERATURE
        super().__init__(spaman, config_entry, automation_entity)
        self._error_count = 0

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        if self.spaman.facade.mrsteam.is_available:
            return "mdi:steam"
        return "mdi:hot-tub"

    @property
    def current_operation(self) -> str:
        """The current operation."""
        return self._automation_entity.current_operation

    @property
    def temperature_unit(self) -> str:
        """Get the current temperature unit."""
        return self._automation_entity.temperature_unit

    @property
    def current_temperature(self) -> float:
        """Get the current temperature."""
        return self._automation_entity.current_temperature

    @property
    def target_temperature(self) -> float:
        """Get the current target temperature."""
        return self._automation_entity.target_temperature

    @property
    def min_temp(self) -> float:
        """Get the minimum temperature."""
        return self._automation_entity.min_temp

    @property
    def max_temp(self) -> float:
        """Get the maximum temperature."""
        return self._automation_entity.max_temp

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature asyncronously."""
        await self._automation_entity.async_set_target_temperature(
            kwargs["temperature"]
        )

    def _on_change(self, _sender: Any, _old_value: Any, _new_value: Any) -> None:
        if self._automation_entity.is_available:
            self._attr_available = True
            self._error_count = 0
        else:
            self._error_count += 1
            if self._error_count > ERROR_COUNT_TOLERANCE:
                self._attr_available = False
        return super()._on_change(_sender, _old_value, _new_value)
