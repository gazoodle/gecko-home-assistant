"""Fan platform for Gecko."""
from geckolib import GeckoPump
from homeassistant.components.fan import SUPPORT_PRESET_MODE, FanEntity

from .const import DOMAIN, ICON
from .entity import GeckoEntity


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    facade = hass.data[DOMAIN][entry.entry_id].facade
    entities = [GeckoFan(entry, pump) for pump in facade.pumps]
    async_add_entities(entities, True)


class GeckoFan(GeckoEntity, FanEntity):
    """gecko fan class."""

    async def async_turn_on(
        self,
        _speed: str | None = None,
        _percentage: int | None = None,
        _preset_mode: str | None = None,
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
