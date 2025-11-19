# Intelar IR Smart Scale for Home Assistant

Custom Home Assistant integration that pulls health metrics (weight, calories, steps, heart rate and more) from the Intelar IR Smart Scale by Tuya using the Tuya Cloud (us.platform.tuya.com).

## Features
- Config flow to authenticate with your Tuya Cloud (access ID/secret and Tuya app credentials)
- Polls the scale's device status via Tuya OpenAPI
- Exposes sensors for weight, BMI, body fat, muscle, water, bone mass, visceral fat, heart rate, calories and step count
- Adjustable polling interval through the integration options

## Installation
1. Copy the `custom_components/intelar_scale` folder into your Home Assistant `config/custom_components` directory.
2. Restart Home Assistant.
3. Go to *Settings → Devices & Services → Add Integration* and search for **Intelar Smart Scale**.
4. Enter your Tuya Cloud credentials (Access ID/Secret), Tuya app login (username/password, country code, app schema) and the device ID for your Intelar scale.

> Tip: Ensure your Tuya Cloud project is bound to your Tuya Smart app account and that the scale is listed as an authorized device in the project.

## Configuration options
- **Endpoint**: Defaults to `https://openapi.tuyaus.com` for the US platform.
- **Scan interval**: Adjust how often the integration polls Tuya for new data (30–3600 seconds).

## Notes
- Credentials are stored in the Home Assistant config entry store. The integration uses Tuya OpenAPI via `tuya-iot-py-sdk` and requires a Tuya Cloud project with the relevant API permissions.
- Only cloud polling is supported; direct local LAN access is not available.
