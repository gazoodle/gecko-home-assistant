"""Switch platform for Gecko."""  # noqa: A005

import logging

from geckolib import GeckoAutomationFacadeBase
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up select platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    if spaman.facade is not None:
        if spaman.facade.heatpump is not None:
            async_add_entities([GeckoHeatPump(spaman, entry, spaman.facade.heatpump)])
        if spaman.facade.ingrid is not None:
            async_add_entities([GeckoInGrid(spaman, entry, spaman.facade.ingrid)])


class GeckoSelect(GeckoEntity, SelectEntity):
    """Gecko select class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        entry: ConfigEntry,
        select: GeckoAutomationFacadeBase,
    ) -> None:
        """Initialize the select."""
        super().__init__(spaman, entry, select)
        _LOGGER.debug("%r loaded. Options are %s", select, select.states)

    @property
    def current_option(self) -> str:
        """Get the current option."""
        return self._automation_entity.state

    @property
    def options(self) -> list[str]:
        """Get the option list."""
        return self._automation_entity.states

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self._automation_entity.async_set_state(option)


class GeckoHeatPump(GeckoSelect):
    """Heat Pump class."""

    @property
    def icon(self) -> str:
        """Get the icon for the heatpump."""
        return "mdi:heat-pump-outline"


class GeckoInGrid(GeckoSelect):
    """InGrid class."""

    @property
    def icon(self) -> str:
        """Get the icon for the heatpump."""
        return "mdi:heat-wave"
