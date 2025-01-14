"""Binary sensor platform for Gecko."""

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntity
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
    """Set up binary_sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            GeckoBinarySensor(spaman, entry, sensor)
            for sensor in spaman.facade.binary_sensors  # type: ignore
        ]
    )


class GeckoBinarySensor(GeckoEntity, BinarySensorEntity):
    """gecko binary_sensor class."""

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        return self._automation_entity.is_on
