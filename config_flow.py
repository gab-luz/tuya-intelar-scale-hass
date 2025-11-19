from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_APP_SCHEMA,
    CONF_COUNTRY_CODE,
    CONF_DEVICE_ID,
    CONF_ENDPOINT,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DEFAULT_ENDPOINT,
    DOMAIN,
)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Intelar Scale"): str,
        vol.Required(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): str,
        vol.Required(CONF_ACCESS_ID): str,
        vol.Required(CONF_ACCESS_SECRET): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_COUNTRY_CODE, default="1"): str,
        vol.Required(CONF_APP_SCHEMA, default="tuyaSmart"): str,
        vol.Required(CONF_DEVICE_ID): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_SCAN_INTERVAL, default=300): vol.All(
            vol.Coerce(int), vol.Range(min=30, max=3600)
        )
    }
)


class IntelarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Intelar scale."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)

        await self._async_set_unique_id(user_input[CONF_DEVICE_ID])
        self._abort_if_unique_id_configured()

        data = user_input.copy()
        name = data.pop(CONF_NAME)

        return self.async_create_entry(title=name, data=data)

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        """Handle import from YAML (not supported)."""

        return await self.async_step_user(user_input)

    async def async_get_options_flow(self, config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        return IntelarOptionsFlow(config_entry)


class IntelarOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Intelar scale."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.config_entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="init", data_schema=OPTIONS_SCHEMA)

        return self.async_create_entry(title="Options", data=user_input)
