"""Fan platform for Gecko."""

from typing import TYPE_CHECKING

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeckoEntity

if TYPE_CHECKING:
    from .spa_manager import GeckoSpaManager


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up fan platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GeckoFan(spaman, entry, pump) for pump in spaman.facade.pumps])


class GeckoFan(GeckoEntity, FanEntity):
    """GeckoFan class."""

    async def async_turn_on(
        self,
        _speed=None,
        _percentage=None,
        _preset_mode=None,
        **_kwargs,
    ) -> None:
        """Turn on the switch."""
        await self._automation_entity.async_set_mode("HI")

    async def async_turn_off(self, **_kwargs) -> None:
        """Turn off the switch."""
        await self._automation_entity.async_set_mode("OFF")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self._automation_entity.async_set_mode(preset_mode)

    @property
    def is_on(self):
        return self.preset_mode != "OFF"

    @property
    def supported_features(self):
        return (
            FanEntityFeature.PRESET_MODE
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
        )

    @property
    def icon(self):
        """Return the icon of this switch."""
        return "mdi:pump"

    @property
    def preset_modes(self):
        return self._automation_entity._user_demand["options"]

    @property
    def preset_mode(self):
        mode = self._automation_entity._state_sensor.state

        if mode != "OFF":
            return mode[0:2]

        return mode
