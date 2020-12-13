"""GeckoEntity class"""
import logging

from homeassistant.helpers.entity import Entity

from .const import DOMAIN, NAME, VERSION

_LOGGER = logging.getLogger(__name__)


class GeckoEntity(Entity):
    def __init__(self, config_entry, automation_entity):
        self.config_entry = config_entry
        self._automation_entity = automation_entity
        self._automation_entity.watch(self._on_change)
        _LOGGER.info(
            f"Setup entity {self._automation_entity.name}/{self._automation_entity.unique_id}"
        )

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
        return {
            "identifiers": {(DOMAIN, self._automation_entity.facade.unique_id)},
            "name": self._automation_entity.facade.name,
            "model": f"{self._automation_entity.facade.spa.pack} {self._automation_entity.facade.spa.version}",
            "manufacturer": NAME,
        }

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            # "time": "**TIME**",  # str(self.coordinator.data.get("time")),
            # "static": "**STATIC**",  # self.coordinator.data.get("static"),
        }

    @property
    def should_poll(self) -> bool:
        """Return false as we're a push model!"""
        return False

    def _on_change(self, sender, old_value, new_value):
        """Notify HA of the change"""
        self.async_schedule_update_ha_state(force_refresh=True)
