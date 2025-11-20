from __future__ import annotations

import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_ID,
    DOMAIN,
    SENSOR_DISPLAY_NAMES,
    SENSOR_TYPES,
)
from .utils import calculate_age_from_birthdate


class IntelarScaleSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Tuya Smart Scale sensor for a specific user."""

    def __init__(self, coordinator, device_id: str, user_id: str, nickname: str | None, entity_type: str) -> None:
        super().__init__(coordinator)
        self.device_id = device_id
        self.user_id = user_id
        self.nickname = nickname
        self.entity_type = entity_type
        self._attr_unique_id = f"{device_id}_{user_id}_{entity_type}"

        display_name = SENSOR_DISPLAY_NAMES.get(entity_type, entity_type.replace("_", " ").title())
        self._attr_name = f"{display_name} ({nickname or user_id})"

        canonical_type = entity_type
        for sensor_type, config in SENSOR_TYPES.items():
            if entity_type == sensor_type or entity_type in config["aliases"]:
                canonical_type = sensor_type
                break

        if canonical_type in SENSOR_TYPES:
            config = SENSOR_TYPES[canonical_type]
            self._attr_native_unit_of_measurement = config["unit"]
            self._attr_device_class = config["device_class"]
            self._attr_icon = config["icon"]

    @property
    def native_value(self):
        user_data = self.coordinator.data.get(self.user_id)
        if not user_data:
            return None

        if self.entity_type == "physical_age":
            birthdate_str = getattr(self.coordinator, "birthdate", None)
            if birthdate_str:
                return calculate_age_from_birthdate(birthdate_str)
            return None

        config = SENSOR_TYPES.get(self.entity_type, {})
        value = user_data.get(self.entity_type)

        if value is None:
            for alias in config.get("aliases", []):
                value = user_data.get(alias)
                if value is not None:
                    break

        if value is None and "analysis_report" in user_data:
            value = user_data["analysis_report"].get(self.entity_type)
            if value is None:
                for alias in config.get("aliases", []):
                    value = user_data["analysis_report"].get(alias)
                    if value is not None:
                        break

        if value is not None:
            if self.entity_type == "body_type":
                body_type_map = {
                    0: "Underweight",
                    1: "Normal",
                    2: "Overweight",
                    3: "Obese",
                    4: "Severely Obese",
                }
                try:
                    return body_type_map.get(int(value), f"Unknown ({value})")
                except (ValueError, TypeError):
                    return value
            if self.entity_type == "create_time":
                try:
                    return datetime.datetime.fromtimestamp(int(value) / 1000, datetime.timezone.utc)
                except (ValueError, TypeError):
                    return None

        return value


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for user_id, user_data in coordinator.data.items():
        nickname = user_data.get("nickname")
        for sensor_type in SENSOR_TYPES.keys():
            entities.append(
                IntelarScaleSensor(
                    coordinator,
                    entry.data[CONF_DEVICE_ID],
                    user_id,
                    nickname,
                    sensor_type,
                )
            )
    async_add_entities(entities)
