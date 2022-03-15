"""Fan platform for Gecko."""
from homeassistant.components.fan import SUPPORT_PRESET_MODE, FanEntity

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup fan platform."""
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
        return SUPPORT_PRESET_MODE

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
