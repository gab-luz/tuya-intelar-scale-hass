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
    COUNTRY_CHOICES,
    CONF_COUNTRY_CODE,
    CONF_DEVICE_ID,
    CONF_ENDPOINT,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    DEFAULT_ENDPOINT,
    DOMAIN,
)

COUNTRY_NAMES = [choice[0] for choice in COUNTRY_CHOICES]

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Intelar Scale"): str,
        vol.Required(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): str,
        vol.Required(CONF_ACCESS_ID): str,
        vol.Required(CONF_ACCESS_SECRET): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_COUNTRY_CODE, default=COUNTRY_NAMES[0]): vol.In(COUNTRY_NAMES),
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

        device_id = user_input[CONF_DEVICE_ID]
        # Enforce uniqueness by device_id without relying on HA internals that vary by release
        for entry in self._async_current_entries():
            if entry.data.get(CONF_DEVICE_ID) == device_id:
                return self.async_abort(reason="already_configured")

        data = user_input.copy()
        name = data.pop(CONF_NAME)
        country_name = data.pop(CONF_COUNTRY_CODE)
        # Convert friendly country selection back to dialing code for Tuya auth
        country_code_lookup = dict(COUNTRY_CHOICES)
        data[CONF_COUNTRY_CODE] = country_code_lookup.get(country_name, country_name)

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
