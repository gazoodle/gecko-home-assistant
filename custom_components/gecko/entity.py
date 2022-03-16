"""GeckoEntity class"""
import logging

from geckolib import Observable
from .spa_manager import GeckoSpaManager
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeckoEntityBase(Entity):
    """Base for all Gecko entities"""

    def __init__(
        self,
        spaman: GeckoSpaManager,
        config_entry: ConfigEntry,
        unique_id: str,
        name: str,
        parent_name: str,
    ) -> None:
        self.spaman = spaman
        self.config_entry = config_entry
        self._unique_id = unique_id
        self._name = name
        self._parent_name = parent_name
        _LOGGER.info("Setup entity %r", self)

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the entity."""
        return f"{self._parent_name}: {self._name}"

    @property
    def device_info(self):
        info = {
            "identifiers": {(DOMAIN, self.spaman.unique_id)},
            "name": self.spaman.spa_name,
            "manufacturer": "Gecko Alliance",
        }
        if self.spaman.facade is not None:
            info["model"] = (
                f"{self.spaman.facade.spa.pack} " f"{self.spaman.facade.spa.version}"
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
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        return None

    @property
    def should_poll(self) -> bool:
        """Return false as we're a push model!"""
        return False

    def __repr__(self):
        return f"{self._name}/{self._unique_id}"


class GeckoEntity(GeckoEntityBase):
    """Entity base of Gecko items"""

    def __init__(
        self, spaman: GeckoSpaManager, config_entry: ConfigEntry, automation_entity
    ):
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

    def _on_change(self, _sender, _old_value, _new_value):
        """Notify HA of the change"""
        if self.hass is not None:
            self.async_schedule_update_ha_state(force_refresh=True)
