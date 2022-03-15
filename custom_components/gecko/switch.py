"""Switch platform for Gecko."""
from geckolib import GeckoBlower, GeckoPump
from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager


async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    entities = [
        GeckoBinarySwitch(spaman, entry, blower) for blower in spaman.facade.blowers
    ]
    if spaman.facade.eco_mode is not None:
        entities.append(GeckoBinarySwitch(spaman, entry, spaman.facade.eco_mode))
    async_add_entities(entities)


class GeckoBinarySwitch(GeckoEntity, SwitchEntity):
    """gecko switch class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self._automation_entity.turn_on()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self._automation_entity.turn_off()

    @property
    def icon(self):
        """Return the icon of this switch."""
        if isinstance(self._automation_entity, GeckoPump):
            return "mdi:pump"
        elif isinstance(self._automation_entity, GeckoBlower):
            return "mdi:fan"
        return "mdi:toggle-switch"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._automation_entity.is_on
