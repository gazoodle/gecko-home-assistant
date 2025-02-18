"""Button platform for Gecko."""

import datetime
import logging

from geckolib.automation.button import GeckoButton as GeckoLibButton
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BUTTON, DOMAIN
from .const import VERSION as INTEGRATION_VERSION
from .entity import GeckoEntity, GeckoEntityBase
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    buttons = []
    if spaman.can_use_facade:
        buttons.append(GeckoSnapshotButton(entry, spaman))
        buttons.extend(
            [
                GeckoKeypadButton(entry, spaman, button)
                for button in spaman.facade.keypad.buttons
            ]
        )
    if spaman.reconnect_button is not None:
        buttons.append(GeckoReconnectButton(entry, spaman))
    async_add_entities(buttons)
    spaman.platform_loaded(BUTTON)


class GeckoButton(GeckoEntity, ButtonEntity):
    """Gecko button class."""


class GeckoKeypadButton(GeckoButton):
    """Gecko keypad button."""

    def __init__(
        self, config_entry: ConfigEntry, spaman: GeckoSpaManager, button: GeckoLibButton
    ) -> None:
        """Initialize the keypad button."""
        super().__init__(spaman, config_entry, button)
        self._button: GeckoLibButton = button

    async def async_press(self) -> None:
        """Press the button asynchronously."""
        await self._button.async_press()


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
            f"{spaman.unique_id}-SNAPSHOT",
            "Snapshot",
            spaman.facade.name,
        )
        self._entity_category = EntityCategory.DIAGNOSTIC

    async def async_press(self) -> None:
        """Press the button asynchronously."""
        facade = self.spaman.facade
        if facade is None:
            return
        data = facade.spa.get_snapshot_data()
        data.update(
            {
                "Integration Version": INTEGRATION_VERSION,
            }
        )
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
