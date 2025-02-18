"""Fan platform for Gecko."""

from typing import TYPE_CHECKING, Any, cast

from geckolib import GeckoBlower, GeckoBubbleGenerator, GeckoPump, GeckoWaterfall
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAN
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
            [
                GeckoFan(spaman, entry, pump)
                for pump in list(spaman.facade.pumps + spaman.facade.blowers)
            ]
        )
    spaman.platform_loaded(FAN)


class GeckoFan(GeckoEntity, FanEntity):
    """GeckoFan class."""

    async def async_turn_on(
        self,
        _speed: str | None = None,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **_kwargs: Any,
    ) -> None:
        """Turn on the switch."""
        await self.pump.async_turn_on(percentage, preset_mode)

    async def async_turn_off(self, **_kwarg: Any) -> None:
        """Turn off the switch."""
        await self.pump.async_turn_off()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        await self.pump.async_turn_on(percentage, None)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the fan preset mode."""
        await self.pump.async_set_mode(preset_mode)

    @property
    def is_on(self) -> bool:
        """Get the fan on/off state."""
        return self.pump.is_on

    @property
    def supported_features(self) -> FanEntityFeature:
        """Get fan supported features."""
        features = FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF
        if self.pump.pump_type == GeckoPump.PumpType.TWO_SPEED:
            features |= FanEntityFeature.PRESET_MODE
        if self.pump.pump_type == GeckoPump.PumpType.VARIABLE_SPEED:
            features |= FanEntityFeature.SET_SPEED
        return features

    @property
    def icon(self) -> str:
        """Return the icon of this switch."""
        if isinstance(self._automation_entity, GeckoBlower):
            return "mdi:fan"
        if isinstance(self._automation_entity, GeckoWaterfall):
            return "mdi:waterfall"
        if isinstance(self._automation_entity, GeckoBubbleGenerator):
            return "mdi:chart-bubble"
        return "mdi:pump"

    @property
    def preset_modes(self) -> list[str]:
        """Get preset modes."""
        return self.pump.modes

    @property
    def preset_mode(self) -> str:
        """Get current preset mode."""
        return self.pump.mode

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.pump.pump_type == GeckoPump.PumpType.VARIABLE_SPEED:
            return self.pump.percentage
        return None

    @property
    def pump(self) -> GeckoPump:
        """Get the pump."""
        return cast(GeckoPump, self._automation_entity)
