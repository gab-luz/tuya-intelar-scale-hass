from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .api import TuyaSmartScaleAPI
from .const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_KEY,
    CONF_BIRTHDATE,
    CONF_DEVICE_ID,
    CONF_REGION,
    CONF_SEX,
    DEFAULT_BIRTHDATE,
    DEFAULT_REGION,
    DEFAULT_SEX,
    DOMAIN,
    REGIONS,
    SEX_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


def _region_options() -> dict[str, str]:
    return {code: data["name"] for code, data in REGIONS.items()}


class IntelarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Intelar scale."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            # Basic duplicate check by device_id
            for entry in self._async_current_entries():
                if entry.data.get(CONF_DEVICE_ID) == user_input.get(CONF_DEVICE_ID):
                    return self.async_abort(reason="already_configured")

            # Validate credentials and device access
            try:
                api = TuyaSmartScaleAPI(
                    access_id=user_input[CONF_ACCESS_ID],
                    access_key=user_input[CONF_ACCESS_KEY],
                    device_id=user_input[CONF_DEVICE_ID],
                    region=user_input.get(CONF_REGION, DEFAULT_REGION),
                    birthdate=user_input.get(CONF_BIRTHDATE, DEFAULT_BIRTHDATE),
                    sex=user_input.get(CONF_SEX, DEFAULT_SEX),
                )
                device_info = await self.hass.async_add_executor_job(api.get_device_info)
                if not device_info:
                    errors["base"] = "cannot_connect"
                else:
                    title = device_info.get("name") or "Intelar Scale"
                    return self.async_create_entry(title=title, data=user_input)
            except ValueError:
                errors[CONF_BIRTHDATE] = "invalid_date"
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.error("Failed to connect to Tuya API: %s", ex)
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ACCESS_ID): str,
                vol.Required(CONF_ACCESS_KEY): str,
                vol.Required(CONF_DEVICE_ID): str,
                vol.Optional(CONF_REGION, default=DEFAULT_REGION): vol.In(_region_options()),
                vol.Optional(CONF_BIRTHDATE, default=DEFAULT_BIRTHDATE): str,
                vol.Optional(CONF_SEX, default=DEFAULT_SEX): vol.In(SEX_OPTIONS),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_import(self, user_input: dict[str, Any]) -> FlowResult:
        return await self.async_step_user(user_input)
