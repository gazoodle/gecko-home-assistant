"""Climate platform for Gecko."""
import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)

from .const import DOMAIN, ICON
from .entity import GeckoEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    facade = hass.data[DOMAIN][entry.entry_id].facade
    async_add_entities(
        [GeckoClimate(entry, facade.water_heater, facade.water_care)], True
    )


class GeckoClimate(GeckoEntity, ClimateEntity):
    """Gecko Climate class."""

    def __init__(self, config_entry, automation_entity, water_care):
        super().__init__(config_entry, automation_entity)
        self._water_care = water_care
        self._water_care.watch(self._on_change)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        features = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

        # if self._client.have_blower():
        #    features |= SUPPORT_FAN_MODE

        return features

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:hot-tub"

    @property
    def hvac_modes(self):
        return [HVAC_MODE_AUTO]

    @property
    def hvac_mode(self):
        return HVAC_MODE_AUTO

    def set_hvac_mode(self, hvac_mode):
        del hvac_mode
        pass

    @property
    def hvac_action(self):
        """The current HVAC action"""
        # I happen to know that the operation modes match HA's modes but
        # they are proper cased, so we just move to lower ...
        return self._automation_entity.current_operation.lower()

    @property
    def preset_modes(self):
        return self._water_care.modes

    @property
    def preset_mode(self):
        if self._water_care.mode is None:
            return "Waiting..."
        return self._water_care.modes[self._water_care.mode]

    def set_preset_mode(self, preset_mode):
        self._water_care.set_mode(preset_mode)

    @property
    def temperature_unit(self):
        return self._automation_entity.temperature_unit

    @property
    def current_temperature(self):
        return self._automation_entity.current_temperature

    @property
    def target_temperature(self):
        return self._automation_entity.target_temperature

    @property
    def min_temp(self):
        return self._automation_entity.min_temp

    @property
    def max_temp(self):
        return self._automation_entity.max_temp

    def set_temperature(self, **kwargs):
        """Set the target temperature"""
        self._automation_entity.set_target_temperature(kwargs["temperature"])
