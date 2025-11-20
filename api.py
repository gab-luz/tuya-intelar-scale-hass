from __future__ import annotations

import logging
from typing import Any

from tuya_iot import TuyaOpenAPI

_LOGGER = logging.getLogger(__name__)


class IntelarScaleApiError(Exception):
    """Raised when the Tuya API returns an error response."""


class IntelarScaleApi:
    """Wrapper around TuyaOpenAPI for the Intelar scale."""

    # Error codes that indicate expired/invalid auth and need a re-login
    _AUTH_ERROR_CODES = {1010, 1100, 1011}

    def __init__(
        self,
        endpoint: str,
        access_id: str,
        access_secret: str,
        username: str,
        password: str,
        country_code: str,
        app_schema: str,
    ) -> None:
        self._endpoint = endpoint
        self._access_id = access_id
        self._access_secret = access_secret
        self._username = username
        self._password = password
        self._country_code = country_code
        self._app_schema = app_schema
        self._api = TuyaOpenAPI(self._endpoint, self._access_id, self._access_secret)
        self._connected = False

    def connect(self) -> None:
        """Connect to Tuya OpenAPI using account credentials."""

        if self._connected:
            return

        _LOGGER.debug("Connecting to Tuya OpenAPI at %s", self._endpoint)
        self._api.connect(
            self._username,
            self._password,
            self._country_code,
            self._app_schema,
        )
        self._connected = True

    def get_device_status(self, device_id: str) -> dict[str, Any]:
        """Return the latest device status payload."""

        for attempt in (1, 2):
            self.connect()
            try:
                result = self._api.get(f"/v1.0/devices/{device_id}/status")
            except Exception as err:  # pylint: disable=broad-except
                self._connected = False
                _LOGGER.error("Tuya API error while fetching status: %s", err)
                if attempt == 1:
                    continue
                raise IntelarScaleApiError(err) from err

            if result.get("success"):
                break

            code = result.get("code")
            if code in self._AUTH_ERROR_CODES and attempt == 1:
                _LOGGER.warning("Tuya token invalid/expired (code %s). Re-authenticating.", code)
                self._connected = False
                continue

            raise IntelarScaleApiError(result)

        status_list: list[dict[str, Any]] = result.get("result", [])
        parsed: dict[str, Any] = {
            item.get("code", ""): item.get("value") for item in status_list
        }
        _LOGGER.debug("Fetched status for %s: %s", device_id, parsed)
        return parsed
