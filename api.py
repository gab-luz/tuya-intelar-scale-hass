"""API client for Tuya Smart Scale integration."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from datetime import date, datetime
from typing import Any, Dict, List

import requests

from .const import CONF_ACCESS_ID, CONF_ACCESS_KEY, REGIONS

_LOGGER = logging.getLogger(__name__)


class TuyaSmartScaleAPI:
    """API client for Tuya Smart Scale."""

    def __init__(
        self,
        access_id: str,
        access_key: str,
        device_id: str,
        region: str = "us",
        birthdate: str = "1990-01-01",
        sex: int = 1,
    ) -> None:
        self.access_id = access_id
        self.access_key = access_key
        self.device_id = device_id
        self.region = region
        self.birthdate = birthdate
        self.sex = sex
        self.endpoint = REGIONS.get(region, REGIONS["us"])["endpoint"]
        self.access_token: str | None = None
        self.token_expires = 0.0
        self.sign_method = "HMAC-SHA256"

        _LOGGER.info(
            "Initialized TuyaSmartScaleAPI with region: %s, endpoint: %s, device_id: %s",
            region,
            self.endpoint,
            device_id,
        )

    def _calculate_age(self) -> int:
        """Calculate current age from stored birthdate."""

        try:
            birth_date = datetime.strptime(self.birthdate, "%Y-%m-%d").date()
            today = date.today()
            return today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
        except (ValueError, TypeError):
            _LOGGER.warning(
                "Invalid birthdate format: %s, using default age 30", self.birthdate
            )
            return 30

    def _sign_request(
        self,
        method: str,
        path: str,
        access_token: str | None = None,
        params: dict[str, Any] | None = None,
        body: str | None = None,
    ) -> tuple[str, str, str]:
        """Sign the request using Tuya v2.0 signature logic."""

        body_sha256 = hashlib.sha256((body or "").encode("utf-8")).hexdigest()
        canonical_path = path
        if params:
            sorted_params = sorted(params.items())
            param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            canonical_path = f"{path}?{param_str}"

        str_to_sign = f"{method}\n{body_sha256}\n\n{canonical_path}"
        timestamp = str(int(time.time() * 1000))
        if access_token:
            message = self.access_id + access_token + timestamp + str_to_sign
        else:
            message = self.access_id + timestamp + str_to_sign

        sign = hmac.new(
            self.access_key.encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest().upper()

        return sign, timestamp, canonical_path

    def get_access_token(self) -> str:
        """Get access token from Tuya API using v2.0 signature logic."""

        if self.access_token and time.time() < self.token_expires - 60:
            return self.access_token

        path = "/v1.0/token?grant_type=1"
        sign, timestamp, canonical_path = self._sign_request(
            "GET", path, access_token=None, params=None
        )
        url = f"{self.endpoint}{canonical_path}"
        headers = {
            "client_id": self.access_id,
            "t": timestamp,
            "sign_method": self.sign_method,
            "sign": sign,
        }
        _LOGGER.debug("Requesting token: url=%s headers=%s", url, headers)
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")

        data = response.json()
        if not isinstance(data, dict) or "result" not in data:
            raise Exception(
                f"Unexpected response structure for access token (missing 'result'): {data}"
            )

        self.access_token = data["result"].get("access_token")
        self.token_expires = time.time() + data["result"].get("expire_time", 0)
        return self.access_token or ""

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        token = self.get_access_token()
        sign, timestamp, canonical_path = self._sign_request(
            "GET", path, access_token=token, params=params
        )
        url = f"{self.endpoint}{canonical_path}"
        headers = {
            "client_id": self.access_id,
            "access_token": token,
            "t": timestamp,
            "sign": sign,
            "sign_method": self.sign_method,
        }
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"GET {path} failed: {response.text}")
        return response.json()

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        token = self.get_access_token()
        body_json = json.dumps(body, separators=(",", ":"))
        sign, timestamp, canonical_path = self._sign_request(
            "POST", path, access_token=token, params=None, body=body_json
        )
        url = f"{self.endpoint}{canonical_path}"
        headers = {
            "client_id": self.access_id,
            "access_token": token,
            "t": timestamp,
            "sign": sign,
            "sign_method": self.sign_method,
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, data=body_json, timeout=15)
        if response.status_code != 200:
            raise Exception(f"POST {path} failed: {response.text}")
        return response.json()

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information."""

        data = self._get(f"/v1.0/devices/{self.device_id}")
        return data.get("result", {})

    def get_scale_records(
        self,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int = 10,
        user_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        """Get scale measurement records."""

        params: dict[str, Any] = {"page_size": limit, "page_no": 1}
        if start_time:
            params["start_time"] = start_time
        data = self._get(f"/v1.0/scales/{self.device_id}/datas/history", params=params)
        result = data.get("result", {})
        records = result.get("records", []) if isinstance(result, dict) else []
        if user_id:
            records = [rec for rec in records if rec.get("user_id") == user_id]
        return records

    def get_scale_users(self) -> List[Dict[str, Any]]:
        """Get users for this scale device by extracting from measurement records."""

        records = self.get_scale_records(limit=100)
        users: dict[str, dict[str, Any]] = {}
        for rec in records:
            user_id = rec.get("user_id")
            nickname = rec.get("nick_name") or rec.get("nickname")
            if user_id and user_id != "0" and user_id.strip() and user_id not in users:
                users[user_id] = {"user_id": user_id, "nickname": nickname}
        return list(users.values())

    def get_analysis_report(
        self, height: float, weight: float, age: int, sex: int, resistance: str
    ) -> Dict[str, Any]:
        """Get body analysis report."""

        body_data = {
            "height": height,
            "weight": weight,
            "age": age,
            "sex": sex,
            "resistance": resistance,
        }
        data = self._post(f"/v1.0/scales/{self.device_id}/analysis-reports", body_data)
        return data.get("result", {})

    def get_latest_data(self) -> Dict[str, Dict[str, Any]]:
        """Get latest measurement data for all users of this scale, including analysis report."""

        users = self.get_scale_users()
        if not users:
            _LOGGER.warning("No users found for this scale device.")
            return {}

        result: dict[str, dict[str, Any]] = {}
        for user in users:
            user_id = user.get("user_id")
            if not user_id:
                continue
            records = self.get_scale_records(user_id=user_id, limit=10)
            if not records:
                continue

            latest_record = records[0]
            record_with_resistance = next(
                (rec for rec in records if rec.get("body_r") and rec.get("body_r") != "0"),
                None,
            )

            try:
                analysis_record = record_with_resistance or latest_record
                height = float(analysis_record.get("height", 0) or 0)
                weight = float(analysis_record.get("wegith", 0) or 0)
                resistance = analysis_record.get("body_r", "0")
                if height > 0 and weight > 0 and resistance and resistance != "0":
                    age = self._calculate_age()
                    analysis_report = self.get_analysis_report(
                        height=height,
                        weight=weight,
                        age=age,
                        sex=self.sex,
                        resistance=resistance,
                    )
                    latest_record["analysis_report"] = analysis_report
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "Could not fetch analysis report for user %s: %s", user_id, err
                )

            latest_record.update({"nickname": user.get("nickname")})
            result[user_id] = latest_record

        return result
