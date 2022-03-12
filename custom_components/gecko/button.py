"""Button platform for Gecko."""
from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [GeckoRestartButton(entry, spaman)],
        True,
    )


class GeckoButton(GeckoEntity, ButtonEntity):
    """Gecko button class."""

    pass


class GeckoRestartButton(GeckoButton):
    def __init__(self, config_entry, spaman) -> None:
        super().__init__(config_entry, spaman.restart_button)

    async def async_press(self) -> None:
        await self._automation_entity.async_press()
