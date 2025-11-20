from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

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
    PLATFORMS,
)
from .coordinator import IntelarScaleDataCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration via YAML (not supported)."""

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Intelar scale from a config entry."""

    api_client = TuyaSmartScaleAPI(
        access_id=entry.data[CONF_ACCESS_ID],
        access_key=entry.data[CONF_ACCESS_KEY],
        device_id=entry.data[CONF_DEVICE_ID],
        region=entry.data.get(CONF_REGION, DEFAULT_REGION),
        birthdate=entry.data.get(CONF_BIRTHDATE, DEFAULT_BIRTHDATE),
        sex=entry.data.get(CONF_SEX, DEFAULT_SEX),
    )

    coordinator = IntelarScaleDataCoordinator(hass, api_client)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, [Platform.SENSOR])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, [Platform.SENSOR]):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
