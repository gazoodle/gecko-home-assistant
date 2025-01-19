"""GeckoEntity class."""

import logging
from typing import Any

from geckolib import GeckoAutomationBase, Observable
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


class GeckoEntityBase(Entity):
    """Base for all Gecko entities."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        unique_id: str,
        name: str,
        parent_name: str,
    ) -> None:
        """Initialize the entity class."""
        self.spaman = spaman
        self.config_entry = config_entry
        self._unique_id = unique_id
        self._name = name
        self._parent_name = parent_name
        self._entity_category: str | None = None
        _LOGGER.info("Setup entity %r", self)

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return f"{self._parent_name}: {self._name}"

    @property
    def device_info(self) -> DeviceInfo | None:
        """Get device information."""
        info = DeviceInfo()
        info["identifiers"] = {(DOMAIN, self.spaman.unique_id)}
        info["name"] = self.spaman.spa_name
        info["manufacturer"] = "Gecko Alliance"
        if self.spaman.facade is not None:
            info["model"] = (
                f"{self.spaman.facade.spa.pack} {self.spaman.facade.spa.version}"
            )
            info["sw_version"] = (
                f"SpaPack:v{self.spaman.facade.spa.revision} "
                f"Config:{self.spaman.facade.spa.config_version} "
                f"Log:{self.spaman.facade.spa.log_version}"
            )
            info["hw_version"] = (
                f"EN:{self.spaman.facade.spa.intouch_version_en} "
                f"CO:{self.spaman.facade.spa.intouch_version_co}"
            )
        return info

    @property
    def entity_category(self) -> str | None:
        """Return the entity category."""
        return self._entity_category

    @property
    def extra_state_attributes(self) -> str | None:
        """Return the extra state attributes."""
        return None

    @property
    def should_poll(self) -> bool:
        """Return false as we're a push model."""
        return False

    def __repr__(self) -> str:
        """Return a unique name."""
        return f"{self._name}/{self._unique_id}"


class GeckoEntity(GeckoEntityBase):
    """Entity base of Gecko items."""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        automation_entity: GeckoAutomationBase,
        entity_category: EntityCategory | None = None,
    ) -> None:
        """Initialize a gecko entity."""
        super().__init__(
            spaman,
            config_entry,
            automation_entity.unique_id,
            automation_entity.name,
            automation_entity.parent_name,
        )
        self._automation_entity = automation_entity
        if isinstance(automation_entity, Observable):
            self._automation_entity.watch(self._on_change)
        if entity_category is not None:
            self._entity_category = entity_category

    def _on_change(self, _sender: Any, _old_value: Any, _new_value: Any) -> None:
        """Notify HA of the change."""
        if self.hass is not None:
            self.async_schedule_update_ha_state(force_refresh=True)
