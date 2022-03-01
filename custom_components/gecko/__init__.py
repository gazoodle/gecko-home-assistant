"""
Custom integration to integrate Gecko with Home Assistant.

For more details about this integration, please refer to
https://github.com/gazoodle/gecko-home-assistant
"""
import asyncio
import logging

from geckolib import GeckoLocator, GeckoAsyncFacade
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant

from .const import (
    CONF_SPA_ADDRESS,
    CONF_SPA_IDENTIFIER,
    CONF_CLIENT_ID,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(_hass: HomeAssistant, _config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    spa_identifier = None
    spa_address = None

    if CONF_SPA_ADDRESS in entry.data:
        spa_address = entry.data.get(CONF_SPA_ADDRESS)
    spa_identifier = entry.data.get(CONF_SPA_IDENTIFIER)
    if CONF_CLIENT_ID in entry.data:
        client_id = entry.data.get(CONF_CLIENT_ID)

    _LOGGER.info(
        "Setup entry for UUID %s, ID %s, address %s",
        client_id,
        spa_identifier,
        spa_address,
    )

    async_facade = GeckoAsyncFacade(
        client_id, spa_identifier=spa_identifier, spa_address=spa_address
    )
    await async_facade.__aenter__()
    datablock = GeckoDataBlock(hass, async_facade, entry)
    hass.data[DOMAIN][entry.entry_id] = datablock

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


class GeckoDataBlock:
    """Data block for Gecko"""

    def __init__(self, hass, facade, entry: ConfigEntry):
        self.hass = hass
        self.facade = facade
        self.facade.watch(self._on_facade_changed)
        self.entry = entry
        self._platforms_created = False

        self.platforms = [
            platform for platform in PLATFORMS if entry.options.get(platform, True)
        ]

    def _on_facade_changed(self, _sender, *_args):
        # if sender is self.facade:
        _LOGGER.debug("Facade status : %s", self.facade.status_line)
        if self.facade.is_ready and not self._platforms_created:
            _LOGGER.info("Facade ready ... create platforms")
            for platform in self.platforms:
                self.hass.async_add_job(
                    self.hass.config_entries.async_forward_entry_setup(
                        self.entry, platform
                    )
                )
            self._platforms_created = True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    datablock = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in datablock.platforms
            ]
        )
    )
    if unloaded:
        _LOGGER.debug("Finalize facade %r", datablock.facade)
        await datablock.facade.__aexit__(None)
        # datablock.facade.complete()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    _LOGGER.info("async_reload_entry called")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
