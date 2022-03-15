"""Switch platform for Gecko."""
from homeassistant.components.light import LightEntity

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [GeckoLight(spaman, entry, light) for light in spaman.facade.lights]
    )


class GeckoLight(GeckoEntity, LightEntity):
    """Gecko light class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self._automation_entity.turn_on()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self._automation_entity.turn_off()

    @property
    def icon(self):
        """Return the icon of this light."""
        return "mdi:lightbulb"

    @property
    def is_on(self):
        """Return true if the light is on."""
        return self._automation_entity.is_on
