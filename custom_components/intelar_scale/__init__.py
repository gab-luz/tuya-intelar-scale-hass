from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import IntelarScaleApi
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
    DATA_CLIENT,
    DATA_COORDINATOR,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the integration via YAML (not supported)."""

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Intelar scale from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    api = IntelarScaleApi(
        entry.data[CONF_ENDPOINT],
        entry.data[CONF_ACCESS_ID],
        entry.data[CONF_ACCESS_SECRET],
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        entry.data[CONF_COUNTRY_CODE],
        entry.data[CONF_APP_SCHEMA],
    )

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL)
    if scan_interval is not None:
        update_interval = timedelta(seconds=scan_interval)
    else:
        update_interval = DEFAULT_SCAN_INTERVAL

    coordinator = IntelarScaleCoordinator(
        hass,
        api,
        entry.data[CONF_DEVICE_ID],
        update_interval,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_CLIENT: api,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


class IntelarScaleCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to poll status from the Tuya API."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: IntelarScaleApi,
        device_id: str,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Intelar Scale",
            update_interval=update_interval,
        )
        self.api = api
        self.device_id = device_id

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.hass.async_add_executor_job(
                self.api.get_device_status, self.device_id
            )
        except Exception as err:  # pylint: disable=broad-except
            raise UpdateFailed(f"Error communicating with Tuya API: {err}") from err
