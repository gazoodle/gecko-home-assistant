"""Switch platform for Gecko."""

from typing import TYPE_CHECKING, Any

from homeassistant.components.light import LightEntity
from homeassistant.components.light.const import ColorMode
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
    """Set up sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    if spaman.facade is not None:
        async_add_entities(
            [GeckoLight(spaman, entry, light) for light in spaman.facade.lights]
        )


class GeckoLight(GeckoEntity, LightEntity):
    """Gecko light class."""

    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        self._automation_entity.turn_on()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        self._automation_entity.turn_off()

    @property
    def icon(self) -> str:
        """Return the icon of this light."""
        return "mdi:lightbulb"

    @property
    def is_on(self) -> bool:
        """Return true if the light is on."""
        return self._automation_entity.is_on
