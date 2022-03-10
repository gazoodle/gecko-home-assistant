"""GeckoSpaManager class manages the interactions between geckolib and HA"""

import logging

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent, GeckoSpaState
from homeassistant.config_entries import HomeAssistant, ConfigEntry
from .const import PLATFORMS, SENSOR
from typing import Optional

_LOGGER = logging.getLogger(__name__)


class GeckoSpaManager(GeckoAsyncSpaMan):
    """HA Gecko Spa Manager"""

    def __init__(
        self,
        client_id: str,
        hass: Optional[HomeAssistant],
        entry: Optional[ConfigEntry],
        **kwargs,
    ):
        super().__init__(client_id, **kwargs)
        self.hass: Optional[HomeAssistant] = hass
        self.entry: Optional[ConfigEntry] = entry

        self._platforms_created = False
        self.platforms = PLATFORMS

        # self.platforms = [
        #    platform for platform in PLATFORMS if entry.options.get(platform, True)
        # ]

        # self.hass.async_add_job(
        #    self.hass.config_entries.async_forward_entry_setup(self.entry, SENSOR)
        # )

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        _LOGGER.debug(f"{event} : {self.spa_state}")
        if (
            event == GeckoSpaEvent.CONNECTION_FINISHED
            and self.spa_state == GeckoSpaState.CONNECTED
            and not self._platforms_created
        ):
            self._build_platforms()

    def _build_platforms(self) -> None:
        assert self.hass is not None
        for platform in self.platforms:
            self.hass.async_add_job(
                self.hass.config_entries.async_forward_entry_setup(self.entry, platform)
            )
        self._platforms_created = True

    def old_on_facade_changed(self, _sender, *_args):
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

    def old_on_facade_status_changed(self, _sender, *_args):
        _LOGGER.debug("Facade status : %s", self.facade.status_line)
