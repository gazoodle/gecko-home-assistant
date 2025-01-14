"""Button platform for Gecko."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
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
    if spaman.reconnect_button is not None:
        async_add_entities([GeckoReconnectButton(entry, spaman)])


class GeckoButton(GeckoEntity, ButtonEntity):
    """Gecko button class."""


class GeckoReconnectButton(GeckoButton):
    """Gecko Reconnect button class."""

    def __init__(self, config_entry: ConfigEntry, spaman: GeckoSpaManager) -> None:
        """Initialize the button class."""
        super().__init__(
            spaman, config_entry, spaman.reconnect_button, EntityCategory.DIAGNOSTIC
        )

    async def async_press(self) -> None:
        """Press the button asynchronously."""
        await self._automation_entity.async_press()

    @property
    def icon(self) -> str:
        """Get the icon for this."""
        return "mdi:connection"
