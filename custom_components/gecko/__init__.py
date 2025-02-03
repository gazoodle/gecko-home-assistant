"""
Custom integration to integrate Gecko Alliance spa with Home Assistant.

For more details about this integration, please refer to
https://github.com/gazoodle/gecko-home-assistant
"""

import logging
import uuid

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_CLIENT_ID,
    CONF_SPA_ADDRESS,
    CONF_SPA_IDENTIFIER,
    CONF_SPA_NAME,
    DOMAIN,
    STARTUP_MESSAGE,
)
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:
        new = {**config_entry.data}
        new[CONF_CLIENT_ID] = f"{uuid.uuid4()}"

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.debug("Migration to version %s successful", config_entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    spa_identifier = None
    spa_address = None
    spa_name = None

    if CONF_SPA_ADDRESS in entry.data:
        spa_address = entry.data.get(CONF_SPA_ADDRESS)
    if CONF_SPA_NAME in entry.data:
        spa_name = entry.data.get(CONF_SPA_NAME)
    spa_identifier = entry.data.get(CONF_SPA_IDENTIFIER)
    client_id = entry.data.get(CONF_CLIENT_ID)

    _LOGGER.debug(
        "Setup entry for UUID %s, ID %s, address %s (%s)",
        client_id,
        spa_identifier,
        spa_address,
        spa_name,
    )

    spaman = GeckoSpaManager(
        client_id,
        hass,
        entry,
        spa_identifier=spa_identifier,
        spa_address=spa_address,
        spa_name=spa_name,
    )
    await spaman.__aenter__()

    hass.data[DOMAIN][entry.entry_id] = spaman

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    spaman: GeckoSpaManager = hass.data[DOMAIN][entry.entry_id]
    unloaded = await spaman.unload_platforms()
    if unloaded:
        _LOGGER.debug("Close SpaMan")
        await spaman.async_reset()
        await spaman.__aexit__()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
