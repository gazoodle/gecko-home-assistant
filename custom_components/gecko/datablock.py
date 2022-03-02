"""GeckoDataBlock class manages various interactions with geckolib and HA"""

import logging

from geckolib import GeckoAsyncFacade
from homeassistant.config_entries import ConfigEntry
from .const import PLATFORMS, SENSOR

_LOGGER = logging.getLogger(__name__)


class GeckoDataBlock:
    """Data block for Gecko"""

    def __init__(self, hass, facade: GeckoAsyncFacade, entry: ConfigEntry):
        self.hass = hass
        self.facade = facade
        self.facade.watch(self._on_facade_changed)
        self.facade.facade_status_sensor.watch(self._on_facade_status_changed)
        self.entry = entry
        self._platforms_created = False

        self.platforms = [
            platform for platform in PLATFORMS if entry.options.get(platform, True)
        ]

        self.hass.async_add_job(
            self.hass.config_entries.async_forward_entry_setup(self.entry, SENSOR)
        )

    def _on_facade_changed(self, _sender, *_args):
        if self.facade.is_ready and not self._platforms_created:
            _LOGGER.info("Facade ready ... unload SENSOR")
            self.hass.async_create_task(
                self.hass.config_entries.async_forward_entry_unload(self.entry, SENSOR)
            )
            _LOGGER.info("Now build all platforms")
            for platform in self.platforms:
                self.hass.async_add_job(
                    self.hass.config_entries.async_forward_entry_setup(
                        self.entry, platform
                    )
                )
            self._platforms_created = True

    def _on_facade_status_changed(self, _sender, *_args):
        _LOGGER.debug("Facade status : %s", self.facade.status_line)
