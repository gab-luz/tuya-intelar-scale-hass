"""Data coordinator for Intelar Smart Scale."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TuyaSmartScaleAPI
from .const import DOMAIN, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class IntelarScaleDataCoordinator(DataUpdateCoordinator):
    """Manage fetching data from the Tuya Smart Scale API."""

    def __init__(self, hass: HomeAssistant, api_client: TuyaSmartScaleAPI, update_seconds: int | None = None) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_seconds or UPDATE_INTERVAL),
        )
        self.api = api_client
        self.birthdate = api_client.birthdate
        self.data: dict[str, dict] = {}

    @property
    def device_ids(self) -> list[str]:
        if not self.data:
            return []
        return list(self.data.keys())

    async def _async_update_data(self) -> dict:
        try:
            return await self.hass.async_add_executor_job(self.api.get_latest_data)
        except Exception as err:  # pylint: disable=broad-except
            raise UpdateFailed(f"Error communicating with Tuya API: {err}") from err
