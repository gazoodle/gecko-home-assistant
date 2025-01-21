"""Button platform for Gecko."""

import datetime
import logging

from geckolib._version import VERSION as LIBRARY_VERSION
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .const import VERSION as INTEGRATION_VERSION
from .entity import GeckoEntity, GeckoEntityBase
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    if spaman.can_use_facade:
        async_add_entities([GeckoSnapshotButton(entry, spaman)])
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


class GeckoSnapshotButton(GeckoEntityBase, ButtonEntity):
    """Gecko Snapshot button class."""

    def __init__(self, config_entry: ConfigEntry, spaman: GeckoSpaManager) -> None:
        """Initialize the button class."""
        super().__init__(
            spaman,
            config_entry,
            f"{spaman.facade.unique_id}-SNAPSHOT",
            "Snapshot",
            spaman.facade.name,
        )
        self._entity_category = EntityCategory.DIAGNOSTIC

    async def async_press(self) -> None:
        """Press the button asynchronously."""
        facade = self.spaman.facade
        if facade is None:
            return
        data = {
            "Integration Version": INTEGRATION_VERSION,
            "Library Version": LIBRARY_VERSION,
            "SpaPackStruct.xml revision": facade.spa.revision,
            "intouch version EN": facade.spa.intouch_version_en,
            "intouch version CO": facade.spa.intouch_version_co,
            "Spa pack": f"{facade.spa.pack} {facade.spa.version}",
            "Low level configuration #": facade.spa.config_number,
            "Config version": facade.spa.config_version,
            "Log version": facade.spa.log_version,
            "Pack type": facade.spa.pack_type,
            "Snapshot UTC Time": f"{datetime.datetime.now(tz=datetime.UTC)}",
            "Status Block": [hex(b) for b in facade.spa.struct.status_block],
        }
        dump = f"SNAPSHOT ========{data}========"
        _LOGGER.info(dump)

        persistent_body = (
            f"A snapshot of your Gecko system was taken at {datetime.datetime.now().astimezone().isoformat()}\n"  # noqa: E501
            f"<details>"
            f"<summary>Click to expand</summary>\n\n"
            f"```{data}```"
            f"</details>"
        )

        # Make a persistent notification so it's easy to access
        await self.hass.services.async_call(
            "notify",
            "persistent_notification",
            service_data={"message": persistent_body, "title": "Gecko Snapshot"},
        )

    @property
    def icon(self) -> str:
        """Get the icon for this."""
        return "mdi:magnify-scan"
