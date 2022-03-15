"""Button platform for Gecko."""
from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    if spaman.reconnect_button is not None:
        async_add_entities([GeckoReconnectButton(entry, spaman)])


class GeckoButton(GeckoEntity, ButtonEntity):
    """Gecko button class."""

    pass


class GeckoReconnectButton(GeckoButton):
    def __init__(self, config_entry, spaman) -> None:
        super().__init__(spaman, config_entry, spaman.reconnect_button)

    async def async_press(self) -> None:
        await self._automation_entity.async_press()

    @property
    def icon(self):
        return "mdi:connection"
