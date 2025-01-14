"""Fan platform for Gecko."""

from typing import TYPE_CHECKING, Any

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
    if spaman.facade is not None:
        async_add_entities(
            [GeckoFan(spaman, entry, pump) for pump in spaman.facade.pumps]
        )


class GeckoFan(GeckoEntity, FanEntity):
    """GeckoFan class."""

    async def async_turn_on(
        self,
        _speed: str | None = None,
        _percentage: int | None = None,
        _preset_mode: int | None = None,
        **_kwargs: Any,
    ) -> None:
        """Turn on the switch."""
        await self._automation_entity.async_set_mode("HI")

    async def async_turn_off(self, **_kwarg: Any) -> None:
        """Turn off the switch."""
        await self._automation_entity.async_set_mode("OFF")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the fan preset mode."""
        await self._automation_entity.async_set_mode(preset_mode)

    @property
    def is_on(self) -> bool:
        """Get the fan on/off state."""
        return self.preset_mode != "OFF"

    @property
    def supported_features(self) -> FanEntityFeature:
        """Get fan supported features."""
        return (
            FanEntityFeature.PRESET_MODE
            | FanEntityFeature.TURN_ON
            | FanEntityFeature.TURN_OFF
        )

    @property
    def icon(self) -> str:
        """Return the icon of this switch."""
        return "mdi:pump"

    @property
    def preset_modes(self) -> list[str]:
        """Get preset modes."""
        return self._automation_entity._user_demand["options"]  # noqa: SLF001

    @property
    def preset_mode(self) -> str:
        """Get current preset mode."""
        mode = self._automation_entity._state_sensor.state  # noqa: SLF001

        if mode != "OFF":
            return mode[0:2]

        return mode
