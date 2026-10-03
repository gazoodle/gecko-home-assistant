"""Climate platform for Gecko."""

import logging
from typing import Any

from geckolib import GeckoAsyncFacade, GeckoWaterCare, GeckoWaterHeater
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CLIMATE, DOMAIN, ERROR_COUNT_TOLERANCE
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
        async_add_entities(
            [
                GeckoClimate(
                    spaman,
                    entry,
                    facade.water_heater,
                    facade.water_care,
                )
            ]
        )
    spaman.platform_loaded(CLIMATE)


class GeckoClimate(GeckoEntity, ClimateEntity):
    """Gecko Climate class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        automation_entity: GeckoWaterHeater,
        water_care: GeckoWaterCare,
    ) -> None:
        """Initialize Gecko climate entity."""
        self._attr_hvac_modes = [HVACMode.AUTO]
        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
        )
        super().__init__(spaman, config_entry, automation_entity)
        self._water_care = water_care
        self._error_count = 0
        if self._water_care.is_available:
            self._water_care.watch(self._on_change)

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return "mdi:hot-tub"

    @property
    def hvac_action(self) -> str:
        """The current HVAC action."""
        # I happen to know that the operation modes match HA's modes but
        # they are proper cased, so we just move to lower ...
        return self._automation_entity.current_operation.lower()

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

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Fake function to set HVAC mode."""

    def _on_change(self, _sender: Any, _old_value: Any, _new_value: Any) -> None:
        if self._automation_entity.is_available:
            self._attr_available = True
            self._error_count = 0
        else:
            self._error_count += 1
            if self._error_count > ERROR_COUNT_TOLERANCE:
                self._attr_available = False
        return super()._on_change(_sender, _old_value, _new_value)
