"""Adds config flow for Gecko."""
import logging
import socket
import uuid

from geckolib import GeckoAsyncFacade
from .spa_manager import GeckoSpaManager
from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol

from .const import (  # pylint: disable=unused-import
    CONF_SPA_ADDRESS,
    CONF_SPA_IDENTIFIER,
    CONF_SPA_NAME,
    CONF_CLIENT_ID,
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
)

_LOGGER = logging.getLogger(__name__)


class GeckoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gecko."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize."""
        _LOGGER.info(STARTUP_MESSAGE)

        self._errors = {}
        self._static_ip = None
        self._client_id = f"{uuid.uuid4()}"
        self._spaman = GeckoSpaManager(self._client_id, None, None)
        # self._facade = GeckoAsyncFacade(self._client_id)

    def async_show_user_form(self):
        """Let the user provide an IP address, or indicate they want us to search for one"""
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
        """Show the select a spa form"""
        _LOGGER.info("Found %s on the network", self._spaman.spa_descriptors)

        # Let the user choose which spa to connect to
        data_schema = {
            vol.Required(
                CONF_SPA_NAME,
            ): vol.In([spa.name for spa in self._spaman.spa_descriptors]),
        }

        return self.async_show_form(
            step_id="pick",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
        )

    async def async_step_user(self, user_input=None):

        _LOGGER.debug("async_step_user user_input = %s", user_input)

        if user_input is None:
            _LOGGER.info("Choose scan or address")
            # await self._facade.__aenter__()
            await self._spaman.__aenter__()
            # Clear errors
            self._errors = {}
            return self.async_show_user_form()

        # We got something as an address ...
        if CONF_SPA_ADDRESS in user_input:
            user_addr = user_input[CONF_SPA_ADDRESS]
            _LOGGER.info("User provided address '%s'", user_addr)

            # Check that this is an IP address, or at least can be interpreted as one
            try:
                socket.inet_aton(user_addr)
            except socket.error:
                self._errors["base"] = "not_ip"
                return self.async_show_user_form()

            # And that there is a spa there to connect to ...
            await self._spaman.async_set_spa_info(user_addr, None, None)
            await self._spaman.wait_for_descriptors()

            if len(self._spaman.spa_descriptors) == 0:
                self._errors["base"] = "no_spa"
                return self.async_show_user_form()

            self._static_ip = user_addr
            self._errors = {}
            return self.async_show_select_form()

        _LOGGER.info("No address provided, so wait for scan to complete...")
        await self._spaman.wait_for_descriptors()
        _LOGGER.info("Scan is complete")

        if len(self._spaman.spa_descriptors) == 0:
            # There are no spas found on your network
            _LOGGER.warning("No spas found on the local network")
            return self.async_abort(reason="no_spas")

        self._errors = {}
        return self.async_show_select_form()

    async def async_step_pick(self, user_input=None):
        """After user has picked a spa"""
        _LOGGER.info("Async step user has picked {%s}", user_input)

        # We have previously selected a spaname from the list, so now
        # connect to the identifier for that spa
        spa_name = user_input[CONF_SPA_NAME]
        _LOGGER.info(
            "Previously, the user selected spa %s to configure, locate it in %s",
            spa_name,
            self._spaman.spa_descriptors,
        )

        spa = next(spa for spa in self._spaman.spa_descriptors if spa.name == spa_name)
        config_data = {
            CONF_SPA_NAME: spa_name,
            CONF_SPA_IDENTIFIER: spa.identifier_as_string,
            CONF_SPA_ADDRESS: self._static_ip,
            CONF_CLIENT_ID: self._client_id,
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
