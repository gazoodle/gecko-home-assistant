"""
Custom integration to integrate Gecko with Home Assistant.

For more details about this integration, please refer to
https://github.com/gazoodle/gecko-home-assistant
"""
import asyncio
import logging
import uuid


from geckolib import GeckoAsyncFacade
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant

from .const import (
    CONF_SPA_ADDRESS,
    CONF_SPA_IDENTIFIER,
    CONF_CLIENT_ID,
    CONF_SPA_NAME,
    DOMAIN,
    STARTUP_MESSAGE,
)
from .datablock import GeckoDataBlock

_LOGGER = logging.getLogger(__name__)


async def async_setup(_hass: HomeAssistant, _config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_migrate_entry(hass, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:

        new = {**config_entry.data}
        new[CONF_CLIENT_ID] = f"{uuid.uuid4()}"

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    spa_identifier = None
    spa_address = None
    spa_name = "Unknown"

    if CONF_SPA_ADDRESS in entry.data:
        spa_address = entry.data.get(CONF_SPA_ADDRESS)
    if CONF_SPA_NAME in entry.data:
        spa_name = entry.data.get(CONF_SPA_NAME)
    spa_identifier = entry.data.get(CONF_SPA_IDENTIFIER)
    client_id = entry.data.get(CONF_CLIENT_ID)

    _LOGGER.info(
        "Setup entry for UUID %s, ID %s, address %s (%s)",
        client_id,
        spa_identifier,
        spa_address,
        spa_name,
    )

    async_facade = GeckoAsyncFacade(
        client_id,
        spa_identifier=spa_identifier,
        spa_address=spa_address,
        spa_name=spa_name,
    )
    await async_facade.__aenter__()
    datablock = GeckoDataBlock(hass, async_facade, entry)
    hass.data[DOMAIN][entry.entry_id] = datablock

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


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
