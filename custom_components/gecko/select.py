"""Switch platform for Gecko."""  # noqa: A005

import logging
from multiprocessing.spawn import spawn_main

from geckolib import GeckoAutomationFacadeBase
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SELECT
from .entity import GeckoEntity
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up select platform."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    if spaman.can_use_facade:
        assert spaman.facade is not None  # noqa: S101
        selects = []
        if spaman.facade.heatpump.is_available:
            selects.append(GeckoHeatPump(spaman, entry, spaman.facade.heatpump))
        if spaman.facade.ingrid.is_available:
            selects.append(GeckoInGrid(spaman, entry, spaman.facade.ingrid))
        if spaman.facade.lockmode.is_available:
            selects.append(GeckoLockMode(spaman, entry, spaman.facade.lockmode))
        if spaman.facade.keypad.backlight.is_available:
            selects.append(
                GeckoKeypadBacklight(spaman, entry, spaman.facade.keypad.backlight)
            )
        if spaman.facade.inmix.is_available and spaman.facade.inmix.syncro.is_available:
            selects.append(GeckoInMixSync(spaman, entry))
        if spaman.facade.water_care.is_available:
            selects.append(GeckoWatercare(spaman, entry))
        if spaman.facade.bainultra.is_available:
            selects.extend(
                [
                    GeckoBainBackrest(spaman, entry, select)
                    for select in spaman.facade.bainultra.selects
                ]
            )
            if spaman.facade.bainultra.chroma.is_available:
                selects.append(
                    GeckoBainChroma(spaman, entry, spaman.facade.bainultra.chroma)
                )
            selects.append(
                GeckoSelect(spaman, entry, spaman.facade.bainultra.drying_cycle)
            )

        async_add_entities(selects)
    spaman.platform_loaded(SELECT)


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
        self._entity_category = EntityCategory.CONFIG
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


class GeckoBainBackrest(GeckoSelect):
    """Bain backrest class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        entry: ConfigEntry,
        select: GeckoAutomationFacadeBase,
    ) -> None:
        """Initialize the backrest select."""
        super().__init__(spaman, entry, select)
        self._entity_category = None

    @property
    def icon(self) -> str:
        """Get the icon for the backrest."""
        return "mdi:heat-wave"


class GeckoBainChroma(GeckoSelect):
    """Bain chroma class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        entry: ConfigEntry,
        select: GeckoAutomationFacadeBase,
    ) -> None:
        """Initialize the chroma select."""
        super().__init__(spaman, entry, select)
        self._entity_category = None

    @property
    def icon(self) -> str:
        """Get the icon for the chroma."""
        return "mdi:looks"


class GeckoLockMode(GeckoSelect):
    """Lockmode class."""

    @property
    def icon(self) -> str:
        """Get the icon for the lock."""
        if self.current_option == "Unlocked":
            return "mdi:lock-open-variant-outline"
        if self.current_option.startswith("Partial"):
            return "mdi:lock-minus-outline"
        return "mdi:lock-outline"


class GeckoKeypadBacklight(GeckoSelect):
    """Keypad Backlight class."""

    @property
    def icon(self) -> str:
        """Get the icon for the keypad."""
        return "mdi:alarm-panel-outline"


class GeckoWatercare(GeckoSelect):
    """Watercare class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the watercare select."""
        super().__init__(spaman, entry, spaman.facade.water_care)

    @property
    def icon(self) -> str:
        """Get the icon for watercare."""
        return "mdi:water-check"


class GeckoInMixSync(GeckoSelect):
    """inMix sync class."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the inmix select."""
        super().__init__(spaman, entry, spaman.facade.inmix.syncro)
        self._entity_category = None

    @property
    def icon(self) -> str:
        """Get the icon for the sync class."""
        return "mdi:alarm-panel-outline"
