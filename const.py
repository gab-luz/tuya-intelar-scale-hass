from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass

DOMAIN = "intelar_scale"
PLATFORMS = ["sensor"]

# API / auth fields
CONF_ACCESS_ID = "access_id"
CONF_ACCESS_KEY = "access_key"
CONF_DEVICE_ID = "device_id"
CONF_REGION = "region"
CONF_BIRTHDATE = "birthdate"
CONF_SEX = "sex"

# Defaults
DEFAULT_REGION = "us"
DEFAULT_BIRTHDATE = "1990-01-01"
DEFAULT_SEX = 1  # 1 = male, 2 = female per Tuya API
UPDATE_INTERVAL = 300  # seconds

# Region definitions
REGIONS = {
    "us": {"name": "United States", "endpoint": "https://openapi.tuyaus.com"},
    "eu": {"name": "Europe", "endpoint": "https://openapi.tuyaeu.com"},
    "cn": {"name": "China", "endpoint": "https://openapi.tuyacn.com"},
    "in": {"name": "India", "endpoint": "https://openapi.tuyain.com"},
}

# Sex options displayed in the UI (maps to API numeric values)
SEX_OPTIONS = {
    1: "Male",
    2: "Female",
}

# Display names for sensors (overrides default title case conversion)
SENSOR_DISPLAY_NAMES = {
    "ffm": "Fat-free Mass",
    "bmi": "BMI",
    "body_r": "Body Resistance",
    "user_id": "User ID",
    "device_id": "Device ID",
    "body_fat": "Body Fat",
    "body_age": "Body Age",
    "body_score": "Body Score",
    "body_type": "Body Type",
    "visceral_fat": "Visceral Fat Index",
    "physical_age": "Physical Age",
    "create_time": "Measurement Time",
    "weight": "Weight",
    "height": "Height",
    "bones": "Bone Mass",
    "muscle": "Muscle Mass",
    "protein": "Protein",
    "water": "Body Water",
    "metabolism": "Basal Metabolic Rate",
}

# Sensor type definitions
SENSOR_TYPES = {
    "weight": {
        "unit": "kg",
        "device_class": SensorDeviceClass.WEIGHT,
        "icon": "mdi:weight-kilogram",
        "aliases": ["wegith"],
    },
    "body_fat": {
        "unit": "%",
        "device_class": None,
        "icon": "mdi:water-percent",
        "aliases": ["fat"],
    },
    "body_r": {
        "unit": "Ω",
        "device_class": None,
        "icon": "mdi:resistor",
        "aliases": [],
    },
    "create_time": {
        "unit": None,
        "device_class": SensorDeviceClass.TIMESTAMP,
        "icon": "mdi:clock",
        "aliases": [],
    },
    "height": {
        "unit": "cm",
        "device_class": None,
        "icon": "mdi:human-male-height",
        "aliases": [],
    },
    "device_id": {
        "unit": None,
        "device_class": None,
        "icon": "mdi:identifier",
        "aliases": [],
    },
    "user_id": {
        "unit": None,
        "device_class": None,
        "icon": "mdi:identifier",
        "aliases": [],
    },
    "nickname": {
        "unit": None,
        "device_class": None,
        "icon": "mdi:identifier",
        "aliases": [],
    },
    "bmi": {
        "unit": None,
        "device_class": None,
        "icon": "mdi:human",
        "aliases": [],
    },
    "body_age": {
        "unit": "years",
        "device_class": None,
        "icon": "mdi:calendar-account",
        "aliases": [],
    },
    "body_score": {
        "unit": None,
        "device_class": None,
        "icon": "mdi:medal",
        "aliases": [],
    },
    "body_type": {
        "unit": None,
        "device_class": None,
        "icon": "mdi:identifier",
        "aliases": [],
    },
    "bones": {
        "unit": "kg",
        "device_class": None,
        "icon": "mdi:weight-lifter",
        "aliases": [],
    },
    "ffm": {
        "unit": "kg",
        "device_class": None,
        "icon": "mdi:weight-lifter",
        "aliases": [],
    },
    "muscle": {
        "unit": "kg",
        "device_class": None,
        "icon": "mdi:weight-lifter",
        "aliases": [],
    },
    "protein": {
        "unit": "%",
        "device_class": None,
        "icon": "mdi:weight-lifter",
        "aliases": [],
    },
    "metabolism": {
        "unit": "kcal/day",
        "device_class": None,
        "icon": "mdi:fire",
        "aliases": [],
    },
    "visceral_fat": {
        "unit": None,
        "device_class": None,
        "icon": "mdi:stomach",
        "aliases": [],
    },
    "water": {
        "unit": "%",
        "device_class": None,
        "icon": "mdi:water-percent",
        "aliases": [],
    },
    "physical_age": {
        "unit": "years",
        "device_class": None,
        "icon": "mdi:calendar-today",
        "aliases": [],
    },
}
