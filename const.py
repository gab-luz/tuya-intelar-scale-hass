from __future__ import annotations

from datetime import timedelta

DOMAIN = "intelar_scale"
PLATFORMS = ["sensor"]
DEFAULT_ENDPOINT = "https://openapi.tuyaus.com"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=5)

CONF_ACCESS_ID = "access_id"
CONF_ACCESS_SECRET = "access_secret"
CONF_ENDPOINT = "endpoint"
CONF_ENDPOINT_FRIENDLY = "endpoint_friendly"
CONF_DEVICE_ID = "device_id"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_COUNTRY_CODE = "country_code"
CONF_APP_SCHEMA = "app_schema"
CONF_SCAN_INTERVAL = "scan_interval"

DATA_COORDINATOR = "coordinator"
DATA_CLIENT = "client"

# Common country selections mapped to their dialing code required by Tuya auth.
COUNTRY_CHOICES: tuple[tuple[str, str], ...] = (
    ("United States / Canada (+1)", "1"),
    ("Brazil (+55)", "55"),
    ("United Kingdom (+44)", "44"),
    ("Ireland (+353)", "353"),
    ("Portugal (+351)", "351"),
    ("Spain (+34)", "34"),
    ("France (+33)", "33"),
    ("Germany (+49)", "49"),
    ("Italy (+39)", "39"),
    ("Australia (+61)", "61"),
    ("New Zealand (+64)", "64"),
)

# Common endpoints grouped by region to avoid typos.
ENDPOINT_CHOICES: tuple[tuple[str, str], ...] = (
    ("United States (Western DC)", "https://openapi.tuyaus.com"),
    ("United States (Western DC, AZ)", "https://openapi-weaz.tuyaus.com"),
    ("Europe", "https://openapi.tuyaeu.com"),
    ("India", "https://openapi.tuyain.com"),
    ("China", "https://openapi.tuyacn.com"),
)

APP_SCHEMAS: tuple[str, ...] = ("tuyaSmart", "smartlife")
