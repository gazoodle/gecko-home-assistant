"""Water heater platform for Gecko."""

import logging
from typing import Any

from geckolib import GeckoAsyncFacade, GeckoWaterCare, GeckoWaterHeater
from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up climate platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    if spaman.facade is not None and spaman.facade.water_heater.is_available:
        facade: GeckoAsyncFacade = spaman.facade
        async_add_entities(
            [
                GeckoHAWaterHeater(
                    spaman,
                    entry,
                    facade.water_heater,
                    facade.water_care,
                )
            ]
        )


class GeckoHAWaterHeater(GeckoEntity, WaterHeaterEntity):
    """Gecko Water Heater class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        automation_entity: GeckoWaterHeater,
        water_care: GeckoWaterCare,
    ) -> None:
        """Initialize Gecko climate entity."""
        self._attr_supported_features = WaterHeaterEntityFeature.TARGET_TEMPERATURE
        super().__init__(spaman, config_entry, automation_entity)
        self._water_care = water_care
        self._water_care.watch(self._on_change)

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:hot-tub"

    @property
    def current_operation(self) -> str:
        """The current operation."""
        return self._automation_entity.current_operation

    @property
    def preset_modes(self) -> list[str] | None:
        """List the water care modes."""
        return self._water_care.modes

    @property
    def preset_mode(self) -> str | None:
        """Get the current preset mode."""
        if self._water_care.mode is None:
            return "Waiting..."
        return self._water_care.modes[self._water_care.mode]

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode asynchronously."""
        await self._water_care.async_set_mode(preset_mode)

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
