from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_ID, DATA_COORDINATOR, DOMAIN


@dataclass
class IntelarScaleSensorEntityDescription(SensorEntityDescription):
    """Describes an Intelar scale sensor."""

    dp_code: str | None = None


SENSORS: tuple[IntelarScaleSensorEntityDescription, ...] = (
    IntelarScaleSensorEntityDescription(
        key="weight",
        name="Weight",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        icon="mdi:scale-bathroom",
        dp_code="weight",
    ),
    IntelarScaleSensorEntityDescription(
        key="bmi",
        name="BMI",
        icon="mdi:human-pregnant",
        dp_code="bmi",
    ),
    IntelarScaleSensorEntityDescription(
        key="bodyfat",
        name="Body Fat",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent-outline",
        dp_code="bodyfat",
    ),
    IntelarScaleSensorEntityDescription(
        key="muscle",
        name="Muscle",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:arm-flex",
        dp_code="muscle",
    ),
    IntelarScaleSensorEntityDescription(
        key="water",
        name="Body Water",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
        dp_code="water",
    ),
    IntelarScaleSensorEntityDescription(
        key="bone_mass",
        name="Bone Mass",
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        icon="mdi:bone",
        dp_code="bone_mass",
    ),
    IntelarScaleSensorEntityDescription(
        key="heart_rate",
        name="Heart Rate",
        icon="mdi:heart-pulse",
        dp_code="heart_rate",
        native_unit_of_measurement="bpm",
    ),
    IntelarScaleSensorEntityDescription(
        key="calories",
        name="Calories",
        icon="mdi:fire",
        dp_code="calories",
        native_unit_of_measurement="kcal",
    ),
    IntelarScaleSensorEntityDescription(
        key="step_count",
        name="Steps",
        icon="mdi:walk",
        dp_code="step_count",
        native_unit_of_measurement="steps",
    ),
    IntelarScaleSensorEntityDescription(
        key="visceral_fat",
        name="Visceral Fat",
        icon="mdi:stomach",
        dp_code="visceral_fat",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    entities: list[IntelarScaleSensor] = []

    for description in SENSORS:
        entities.append(
            IntelarScaleSensor(
                coordinator=coordinator,
                description=description,
                device_id=entry.data[CONF_DEVICE_ID],
                name=entry.title,
            )
        )

    async_add_entities(entities)


class IntelarScaleSensor(CoordinatorEntity, SensorEntity):
    entity_description: IntelarScaleSensorEntityDescription

    def __init__(
        self,
        coordinator,
        description: IntelarScaleSensorEntityDescription,
        device_id: str,
        name: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"
        self._attr_name = f"{name} {description.name}"
        self._device_id = device_id

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            manufacturer="Tuya",
            model="Intelar IR Smart Scale",
            name=name,
        )

    @property
    def native_value(self) -> Any:
        data: dict[str, Any] | None = self.coordinator.data
        if not data:
            return None

        if self.entity_description.dp_code:
            return data.get(self.entity_description.dp_code)
        return data.get(self.entity_description.key)
