"""Switch platform for Gecko."""

from typing import TYPE_CHECKING, Any

from geckolib import GeckoBlower, GeckoPump
from homeassistant.components.switch import SwitchEntity
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
        entities = [
            GeckoBinarySwitch(spaman, entry, blower) for blower in spaman.facade.blowers
        ]
        if spaman.facade.eco_mode is not None:
            entities.append(GeckoBinarySwitch(spaman, entry, spaman.facade.eco_mode))
        async_add_entities(entities)


class GeckoBinarySwitch(GeckoEntity, SwitchEntity):
    """Gecko switch class."""

    async def async_turn_on(self, **_kwargs: Any) -> None:
        """Turn on the switch."""
        await self._automation_entity.async_turn_on()

    async def async_turn_off(self, **_kwargs: Any) -> None:
        """Turn off the switch."""
        await self._automation_entity.async_turn_off()

    @property
    def icon(self) -> str:
        """Return the icon of this switch."""
        if isinstance(self._automation_entity, GeckoPump):
            return "mdi:pump"
        if isinstance(self._automation_entity, GeckoBlower):
            return "mdi:fan"
        return "mdi:toggle-switch"

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self._automation_entity.is_on
