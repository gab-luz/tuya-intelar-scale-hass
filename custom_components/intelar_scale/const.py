from __future__ import annotations

from datetime import timedelta

DOMAIN = "intelar_scale"
PLATFORMS = ["sensor"]
DEFAULT_ENDPOINT = "https://openapi.tuyaus.com"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_ENDPOINT = "endpoint"
CONF_DEVICE_ID = "device_id"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_COUNTRY_CODE = "country_code"
CONF_APP_SCHEMA = "app_schema"
CONF_SCAN_INTERVAL = "scan_interval"

DATA_COORDINATOR = "coordinator"
DATA_CLIENT = "client"
