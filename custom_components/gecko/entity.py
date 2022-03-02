"""GeckoEntity class"""
import logging

from homeassistant.helpers.entity import Entity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class GeckoEntity(Entity):
    """Entity base of Gecko items"""

    def __init__(self, config_entry, automation_entity):
        self.config_entry = config_entry
        self._automation_entity = automation_entity
        self._automation_entity.watch(self._on_change)
        _LOGGER.info("Setup entity %r", self)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return f"{self._automation_entity.unique_id}"

    @property
    def name(self):
        """Return the name of the entity."""
        return f"{self._automation_entity.facade.name}: {self._automation_entity.name}"

    @property
    def device_info(self):
        if self._automation_entity.facade.is_ready:
            return {
                "identifiers": {(DOMAIN, self._automation_entity.facade.unique_id)},
                "name": self._automation_entity.facade.name,
                "model": (
                    f"{self._automation_entity.facade.spa.pack} "
                    f"{self._automation_entity.facade.spa.version}"
                ),
                "manufacturer": "Gecko Alliance",
                "sw_version": (
                    f"SpaPack:v{self._automation_entity.facade.spa.revision} "
                    f"Config:{self._automation_entity.facade.spa.config_version} "
                    f"Log:{self._automation_entity.facade.spa.log_version}"
                ),
                "hw_version": (
                    f"EN:{self._automation_entity.facade.spa.intouch_version_en} "
                    f"CO:{self._automation_entity.facade.spa.intouch_version_co}"
                ),
            }
        return {
            "identifiers": {(DOMAIN, self._automation_entity.facade.unique_id)},
        }

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        return None

    @property
    def should_poll(self) -> bool:
        """Return false as we're a push model!"""
        return False

    def _on_change(self, _sender, _old_value, _new_value):
        """Notify HA of the change"""
        self.async_schedule_update_ha_state(force_refresh=True)

    def __repr__(self):
        return f"{self._automation_entity.name}/{self._automation_entity.unique_id}"
