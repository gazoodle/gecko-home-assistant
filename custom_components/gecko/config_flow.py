"""Adds config flow for Gecko."""

import logging
import socket
import uuid
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry, ConfigFlowResult
from homeassistant.core import callback

from .const import (  # pylint: disable=unused-import
    CONF_CLIENT_ID,
    CONF_SPA_ADDRESS,
    CONF_SPA_IDENTIFIER,
    CONF_SPA_NAME,
    DOMAIN,
    SHOW_PING_KEY,
    STARTUP_MESSAGE,
)
from .spa_manager import GeckoSpaManager

_LOGGER = logging.getLogger(__name__)


class GeckoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gecko."""

    VERSION = 2
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self) -> None:
        """Initialize the flow handler class."""
        _LOGGER.info(STARTUP_MESSAGE)

        self._errors = {}
        self._static_ip = None
        self._client_id = f"{uuid.uuid4()}"
        self._spaman = GeckoSpaManager(self._client_id, None, None)

    def async_show_user_form(self) -> ConfigFlowResult:
        """Let the user provide an IP address, or indicate they want to search."""
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

    def async_show_select_form(self) -> ConfigFlowResult:
        """Show the select a spa form."""
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

    async def _async_step_with_address(self, user_addr: str) -> ConfigFlowResult:
        # Check that this is an IP address, or at least can be interpreted as one
        try:
            socket.inet_aton(user_addr)
        except OSError:
            self._errors["base"] = "not_ip"
            return self.async_show_user_form()

        # And that there is a spa there to connect to ...
        await self._spaman.async_set_spa_info(user_addr, None, None)
        await self._spaman.wait_for_descriptors()

        if self._spaman.spa_descriptors is None:
            self._errors["base"] = "no_spa"
            return self.async_show_user_form()

        if len(self._spaman.spa_descriptors) == 0:
            self._errors["base"] = "no_spa"
            return self.async_show_user_form()

        self._static_ip = user_addr
        self._errors = {}
        return self.async_show_select_form()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask user to take next step."""
        _LOGGER.debug("async_step_user user_input = %s", user_input)

        if user_input is None:
            _LOGGER.info("Choose scan or address")
            await self._spaman.__aenter__()
            # Clear errors
            self._errors = {}
            return self.async_show_user_form()

        # We got something as an address ...
        if CONF_SPA_ADDRESS in user_input:
            user_addr = user_input[CONF_SPA_ADDRESS]
            _LOGGER.info("User provided address '%s'", user_addr)
            return await self._async_step_with_address(user_addr)

        _LOGGER.info("No address provided, so wait for scan to complete...")
        await self._spaman.wait_for_descriptors()
        _LOGGER.info("Scan is complete")

        if self._spaman.spa_descriptors is None:
            # There are no spas found on your network
            _LOGGER.warning("No spas found on the local network")
            return self.async_abort(reason="no_spas")

        if len(self._spaman.spa_descriptors) == 0:
            # There are no spas found on your network
            _LOGGER.warning("No spas found on the local network")
            return self.async_abort(reason="no_spas")

        self._errors = {}
        return self.async_show_select_form()

    async def async_step_pick(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """After user has picked a spa."""
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
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Get options flow implementation class."""
        return GeckoOptionsFlowHandler(config_entry)


class GeckoOptionsFlowHandler(config_entries.OptionsFlow):
    """Gecko config flow options handler."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> ConfigFlowResult:
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        SHOW_PING_KEY, default=self.options.get(SHOW_PING_KEY, False)
                    ): bool
                }
            ),
        )

    async def _update_options(self) -> ConfigFlowResult:
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_SPA_NAME), data=self.options
        )
