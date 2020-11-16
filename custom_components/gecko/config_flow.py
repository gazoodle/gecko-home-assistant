"""Adds config flow for Gecko."""
from homeassistant import config_entries
from homeassistant.core import callback

import voluptuous as vol
from geckolib import GeckoLocator

from .const import (  # pylint: disable=unused-import
    CONF_SPA_NAME,
    CONF_SPA_IDENTIFIER,
    DOMAIN,
    PLATFORMS,
    GECKOLIB_MANAGER_UUID,
)


class GeckoFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Gecko."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self):
        """Initialize."""
        self._errors = {}
        with GeckoLocator(GECKOLIB_MANAGER_UUID) as locator:
            self.spas = locator.spas

    def _get_spa_identifier(self, spa_name):
        return next(spa for spa in self.spas if spa.name == spa_name).identifier

    async def async_step_user(self, user_input=None):

        """Handle a flow initialized by the user."""
        self._errors = {}

        if len(self.spas) == 0:
            # There are no spas found on your network
            return self.async_abort(reason="no_spas")

        elif len(self.spas) == 1:
            # There was just one spa, so go ahead and
            config_data = {CONF_SPA_IDENTIFIER: self.spas[0].identifier}
            return self.async_create_entry(title=self.spas[0].name, data=config_data)

        elif user_input is not None:
            # We have previously selected a spaname from the list, so now
            # connect to the identifier for that spa
            config_data = {
                CONF_SPA_IDENTIFIER: self._get_spa_identifier(
                    user_input[CONF_SPA_NAME]
                ),
            }
            return self.async_create_entry(
                title=user_input[CONF_SPA_NAME], data=config_data
            )

        else:
            # Let the user choose which spa to connect to
            data_schema = {
                vol.Required(
                    CONF_SPA_NAME,
                ): vol.In([spa.name for spa in self.spas]),
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
