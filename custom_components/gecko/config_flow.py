"""Adds config flow for Gecko."""
import asyncio
import logging

from geckolib import GeckoLocator
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import (  # pylint: disable=unused-import
    CONF_SPA_IDENTIFIER,
    CONF_SPA_NAME,
    DOMAIN,
    GECKOLIB_MANAGER_UUID,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


class GeckoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gecko."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize."""
        self._errors = {}
        self._locator = GeckoLocator(GECKOLIB_MANAGER_UUID)
        self._locator.start_discovery()

    async def async_step_user(self, user_input=None):

        _LOGGER.info(f"Async step user, we have {self._locator}")

        # Wait for locator to have had sufficient time to find something
        while not self._locator.has_had_enough_time:
            await asyncio.sleep(1)
        self._locator.complete()

        """Handle a flow initialized by the user."""
        self._errors = {}

        if len(self._locator.spas) == 0:
            # There are no spas found on your network
            _LOGGER.warning("No spas found on the local network")
            return self.async_abort(reason="no_spas")

        elif len(self._locator.spas) == 1:
            # There was just one spa, so go ahead and use that
            spa = self._locator.spas[0]
            _LOGGER.info("Only one spa (%r) found", spa)
            config_data = {CONF_SPA_IDENTIFIER: spa.identifier_as_string}
            return self.async_create_entry(title=spa.name, data=config_data)

        elif user_input is not None:
            # We have previously selected a spaname from the list, so now
            # connect to the identifier for that spa
            spa_name = user_input[CONF_SPA_NAME]
            _LOGGER.info(
                "Previously, the user selected spa %s to configure, locate it in %r",
                spa_name,
                self._locator,
            )
            config_data = {
                CONF_SPA_IDENTIFIER: self._locator.get_spa_from_name(
                    spa_name
                ).identifier_as_string,
            }
            return self.async_create_entry(
                title=user_input[CONF_SPA_NAME], data=config_data
            )

        else:
            # Let the user choose which spa to connect to
            data_schema = {
                vol.Required(
                    CONF_SPA_NAME,
                ): vol.In([spa.name for spa in self._locator.spas]),
            }

            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(data_schema),
                errors=self._errors,
            )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return GeckoOptionsFlowHandler(config_entry)


class GeckoOptionsFlowHandler(config_entries.OptionsFlow):
    """Gecko config flow options handler."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_SPA_NAME), data=self.options
        )
