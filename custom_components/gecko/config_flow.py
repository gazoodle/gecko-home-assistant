"""Adds config flow for Gecko."""
import asyncio
import logging
import socket

from geckolib import GeckoLocator
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import (  # pylint: disable=unused-import
    CONF_SPA_ADDRESS,
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
        self._static_ip = None
        _LOGGER.info("Gecko scan started")
        self._locator = GeckoLocator(GECKOLIB_MANAGER_UUID)
        self._locator.start_discovery()

    def async_show_user_form(self):
        # Let the user provide an IP address, or indicate they want us to search for one
        data_schema = {
            vol.Optional(
                CONF_SPA_ADDRESS,
            ): str,
        }
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
        )

    def async_show_select_form(self):
        _LOGGER.info(f"Found {self._locator.spas} on the network")

        # Let the user choose which spa to connect to
        data_schema = {
            vol.Required(
                CONF_SPA_NAME,
            ): vol.In([spa.name for spa in self._locator.spas]),
        }

        return self.async_show_form(
            step_id="pick",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
        )

    async def async_step_user(self, user_input=None):

        if user_input == None:
            _LOGGER.info("Choose scan or address")
            # Clear errors
            self._errors = {}
            return self.async_show_user_form()

        # We got something as an address ...
        if CONF_SPA_ADDRESS in user_input:
            user_addr = user_input[CONF_SPA_ADDRESS]
            _LOGGER.info(f"User provided address '{user_addr}'")
            # Don't need existing locator anymore
            self._locator.complete()

            # Check that this is an IP address, or at least can be interpreted as one
            try:
                socket.inet_aton(user_addr)
            except socket.error:
                self._errors["base"] = "not_ip"
                return self.async_show_user_form()

            # And that there is a spa there to connect to ...
            self._locator = GeckoLocator(GECKOLIB_MANAGER_UUID, static_ip=user_addr)
            self._locator.start_discovery(True)
            self._locator.complete()

            if len(self._locator.spas) == 0:
                self._errors["base"] = "no_spa"
                return self.async_show_user_form()

            self._static_ip = user_addr
            self._errors = {}
            return self.async_show_select_form()

        _LOGGER.info(f"No address provided, so wait for scan to complete...")
        while not self._locator.has_had_enough_time:
            await asyncio.sleep(0.1)
        self._locator.complete()
        _LOGGER.info("Scan is complete")

        if len(self._locator.spas) == 0:
            # There are no spas found on your network
            _LOGGER.warning("No spas found on the local network")
            return self.async_abort(reason="no_spas")

        self._errors = {}
        return self.async_show_select_form()

    async def async_step_pick(self, user_input=None):
        _LOGGER.info(f"Async step user has picked {user_input}")

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
            CONF_SPA_ADDRESS: self._static_ip,
        }
        return self.async_create_entry(
            title=user_input[CONF_SPA_NAME], data=config_data
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
