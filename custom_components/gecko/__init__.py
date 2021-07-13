"""
Custom integration to integrate Gecko with Home Assistant.

For more details about this integration, please refer to
https://github.com/gazoodle/gecko-home-assistant
"""
import asyncio
from datetime import timedelta
import logging

from geckolib import GeckoLocator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant

from .const import (
    CONF_SPA_IDENTIFIER,
    DOMAIN,
    GECKOLIB_MANAGER_UUID,
    PLATFORMS,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    spa_identifier = entry.data.get(CONF_SPA_IDENTIFIER)
    _LOGGER.info("Setup entry for %s", spa_identifier)

    with GeckoLocator(GECKOLIB_MANAGER_UUID, spa_to_find=spa_identifier) as locator:
        _LOGGER.info("Locator %s ready", locator)
        try:
            spa = await hass.async_add_executor_job(
                locator.get_spa_from_identifier, spa_identifier
            )
            facade = await hass.async_add_executor_job(spa.get_facade, False)
            _LOGGER.info("Waiting for facade to be ready")
            while not facade.is_connected:
                await asyncio.sleep(0.1)
            _LOGGER.info("Facade is ready")
            datablock = GeckoDataBlock(facade, entry)
            hass.data[DOMAIN][entry.entry_id] = datablock
        except Exception:
            _LOGGER.exception("Exception during entry setup")
            return False

        for platform in datablock.platforms:
            hass.async_add_job(
                hass.config_entries.async_forward_entry_setup(entry, platform)
            )

        entry.add_update_listener(async_reload_entry)
    return True


class GeckoDataBlock:
    def __init__(self, facade, entry: ConfigEntry):
        self.facade = facade
        self.platforms = [
            platform for platform in PLATFORMS if entry.options.get(platform, True)
        ]


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
        datablock.facade.complete()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    _LOGGER.info("async_reload_entry called")
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
