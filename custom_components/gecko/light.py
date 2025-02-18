"""Switch platform for Gecko."""

from typing import Any, cast

from geckolib import GeckoAutomationFacadeBase, GeckoInMixZone
from homeassistant.components.light import LightEntity
from homeassistant.components.light.const import ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LIGHT
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
        if spaman.facade.inmix.is_available:
            async_add_entities(
                [GeckoZone(spaman, entry, zone) for zone in spaman.facade.inmix.zones]
            )
    spaman.platform_loaded(LIGHT)


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


class GeckoZone(GeckoEntity, LightEntity):
    """Gecko zone class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        entry: ConfigEntry,
        zone: GeckoAutomationFacadeBase,
    ) -> None:
        """Initialize the zone."""
        super().__init__(spaman, entry, zone)
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_color_modes = {ColorMode.RGB}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the switch."""
        await self._zone.async_turn_on(**kwargs)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the switch."""
        await self._zone.async_turn_off(**kwargs)

    @property
    def icon(self) -> str:
        """Return the icon of this light."""
        return "mdi:lightbulb"

    @property
    def is_on(self) -> bool:
        """Return true if the light is on."""
        return self._zone.is_on

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        """Get the rgb colour."""
        return self._zone.rgb_color

    @property
    def brightness(self) -> int | None:
        """Get the brightness."""
        return self._zone.brightness

    @property
    def _zone(self) -> GeckoInMixZone:
        return cast(GeckoInMixZone, self._automation_entity)
