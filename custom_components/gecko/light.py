"""Switch platform for Gecko."""

from typing import Any

from geckolib import GeckoAutomationFacadeBase
from homeassistant.components.light import LightEntity
from homeassistant.components.light.const import ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeckoEntity
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

    def __init__(
        self,
        spaman: GeckoSpaManager,
        entry: ConfigEntry,
        light: GeckoAutomationFacadeBase,
    ) -> None:
        """Initialize the light."""
        super().__init__(spaman, entry, light)
        self._attr_color_mode = ColorMode.ONOFF
        self._attr_supported_color_modes = {ColorMode.ONOFF}

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn on the switch."""
        await self._automation_entity.async_turn_on()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn off the switch."""
        await self._automation_entity.async_turn_off()

    @property
    def icon(self) -> str:
        """Return the icon of this light."""
        return "mdi:lightbulb"

    @property
    def is_on(self) -> bool:
        """Return true if the light is on."""
        return self._automation_entity.is_on
