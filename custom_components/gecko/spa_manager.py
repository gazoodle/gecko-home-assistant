"""GeckoSpaManager class manages the interactions between geckolib and HA"""

import asyncio
import logging

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent, GeckoSpaState
from homeassistant.config_entries import HomeAssistant, ConfigEntry
from .const import PLATFORMS, SENSOR, BUTTON
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

        self.platforms = []

    async def handle_event(self, event: GeckoSpaEvent, **kwargs) -> None:
        _LOGGER.debug(f"{event} : {self.spa_state}")

        if event in (
            GeckoSpaEvent.CONNECTION_FINISHED,
            GeckoSpaEvent.RUNNING_SPA_DISCONNECTED,
            GeckoSpaEvent.ERROR_RF_ERROR,
            GeckoSpaEvent.RUNNING_PING_NO_RESPONSE,
        ):
            await self._build_platforms()

    async def _build_platforms(self) -> None:
        assert self.hass is not None

        _LOGGER.debug("Build platforms")

        # Kill all existing platforms
        for platform in self.platforms:
            self.hass.async_add_job(
                self.hass.config_entries.async_forward_entry_unload(
                    self.entry, platform
                )
            )
        if self.platforms:
            await asyncio.sleep(1)
        self.platforms = []

        if self.spa_state == GeckoSpaState.CONNECTED:
            for platform in PLATFORMS:
                self.hass.async_add_job(
                    self.hass.config_entries.async_forward_entry_setup(
                        self.entry, platform
                    )
                )
                self.platforms.append(platform)
        else:
            self.hass.async_add_job(
                self.hass.config_entries.async_forward_entry_setup(self.entry, BUTTON)
            )
            self.hass.async_add_job(
                self.hass.config_entries.async_forward_entry_setup(self.entry, SENSOR)
            )
            self.platforms.append(BUTTON)
            self.platforms.append(SENSOR)
