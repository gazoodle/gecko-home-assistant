"""GeckoSpaManager class manages the interactions between geckolib and HA."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Self

from geckolib import GeckoAsyncSpaMan, GeckoSpaEvent

from .const import (
    BUTTON,
    PLATFORMS,
    SENSOR,
    SHOW_PING_KEY,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class GeckoSpaManager(GeckoAsyncSpaMan):
    """HA Gecko Spa Manager."""

    def __init__(
        self,
        client_id: str,
        hass: HomeAssistant | None,
        entry: ConfigEntry | None,
        **kwargs: Any,
    ) -> None:
        """Initialize the Spa Manager."""
        super().__init__(client_id, **kwargs)
        self.hass: HomeAssistant | None = hass
        self.entry: ConfigEntry | None = entry

        self._can_use_facade = False

        self.platforms = []
        self._event_queue: asyncio.Queue = asyncio.Queue()

    async def __aenter__(self) -> Self:
        """Perform async enter."""
        await super().__aenter__()
        self.add_task(
            self._queue_loop(), "Home Assistant Gecko Spa Manager", "HASPAMAN"
        )
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        """Support async with."""
        self.cancel_key_tasks("HASPAMAN")
        return await super().__aexit__(*exc_info)

    @property
    def can_use_facade(self) -> bool:
        """Determine if the facade is ready for use."""
        return self._can_use_facade

    async def _queue_loop(self) -> None:
        while True:
            event = await self._event_queue.get()
            if event == GeckoSpaEvent.CLIENT_FACADE_IS_READY:
                # Wait for a single update so we have reminders and watercare
                await self.facade.wait_for_one_update()
                self._can_use_facade = True
                await self.reload()

            elif event in [
                GeckoSpaEvent.CLIENT_HAS_RECONNECT_BUTTON,
                GeckoSpaEvent.CLIENT_HAS_STATUS_SENSOR,
            ]:
                await self.reload()

            elif event == GeckoSpaEvent.CLIENT_FACADE_TEARDOWN:
                self._can_use_facade = False
                await self.reload()

    async def handle_event(self, event: GeckoSpaEvent, **_kwargs: Any) -> None:
        """Handle spa manager events."""
        _LOGGER.debug("Event: %s, state %s", event, self.spa_state)
        # The Geckolib spa manager issues events as they happen, and sometimes
        # this is what you want, but for HA, we want to serialise some of them
        # because otherwise we end up trying to build platforms at the same time
        await self._event_queue.put(event)

    async def unload_platforms(self) -> bool:
        """Unload the platforms that were previously loaded."""
        if self.platforms:
            _LOGGER.debug("Unload platforms %s", self.platforms)

            unloaded: bool = await self.hass.config_entries.async_unload_platforms(
                self.entry, self.platforms
            )
            self.platforms = []
            return unloaded
        return True

    async def load_platforms(self) -> None:
        """Load the appropriate platforms."""
        platforms = [SENSOR, BUTTON]
        if self._can_use_facade:
            platforms = PLATFORMS
        self.platforms = platforms

        _LOGGER.debug("Load platforms %s", platforms)
        await self.hass.config_entries.async_forward_entry_setups(self.entry, platforms)

    def platform_loaded(self, platform: str) -> None:
        """Call when a platform has loaded."""
        if platform not in self.platforms:
            self.platforms.append(platform)

    async def reload(self) -> None:
        """Reload the platforms."""
        await self.unload_platforms()
        await self.load_platforms()

    @property
    def show_ping_sensor(self) -> bool:
        """Show the ping sensor property."""
        if SHOW_PING_KEY not in self.entry.options:
            return False
        return self.entry.options[SHOW_PING_KEY]
