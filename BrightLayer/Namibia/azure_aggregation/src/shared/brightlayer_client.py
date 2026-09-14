from __future__ import annotations

from typing import Any, Dict, List, Optional

import requests

from .retry_policy import with_retry

TOKEN_PATH = "/api/v1/auth/serviceaccount/token"
REALTIME_PATH = "/api/v1/dashboard/devices/{device_id}/realtime"
TIMESERIES_PATH = "/api/v1/dashboard/devices/timeseries"
DEVICES_PATH = "/api/v1/dashboard/organization/{organization_id}/devices"


class BrightlayerAuthError(RuntimeError):
    """Raised when the Brightlayer service account token request fails."""


class BrightlayerClient:
    """REST client for the Brightlayer dashboard API (read-only telemetry surface).

    Covers the endpoints documented in "API Documentation example Boreal":
    service account token, realtime, timeseries, and organization device lookup.
    Writeback of aggregate KPIs is NOT part of this client — Brightlayer has no
    REST ingestion endpoint for telemetry, so writeback uses Azure IoT Hub MQTT
    (see modules/writeback_to_brightlayer.py).
    """

    def __init__(
        self,
        api_prefix: str,
        service_account_id: str,
        service_account_secret: str,
        max_retries: int = 3,
        retry_base_seconds: int = 10,
        session: Optional[requests.Session] = None,
    ):
        self.api_prefix = api_prefix.rstrip("/")
        self.service_account_id = service_account_id
        self.service_account_secret = service_account_secret
        self.max_retries = max_retries
        self.retry_base_seconds = retry_base_seconds
        self.session = session or requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "BrightlayerAggregation/1.0",
        })
        self._token: Optional[str] = None

    def get_token(self, force_refresh: bool = False) -> str:
        """Fetch (or return cached) service account bearer token."""
        if self._token is not None and not force_refresh:
            return self._token

        def _fetch() -> str:
            response = self.session.post(
                f"{self.api_prefix}{TOKEN_PATH}",
                json={
                    "serviceAccountId": self.service_account_id,
                    "secret": self.service_account_secret,
                },
                timeout=30,
            )
            if response.status_code != 200:
                raise BrightlayerAuthError(
                    f"Token request failed with status {response.status_code}: {response.text}"
                )
            token = response.json().get("token")
            if not token:
                raise BrightlayerAuthError("Token response did not contain a 'token' field.")
            return token

        self._token = with_retry(_fetch, self.max_retries, self.retry_base_seconds)
        return self._token

    def _authorized_request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        def _do_request() -> requests.Response:
            headers = kwargs.pop("headers", {}) or {}
            headers["Authorization"] = f"Bearer {self.get_token()}"
            response = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
            if response.status_code == 401:
                # Token may have expired; refresh once and retry within this attempt.
                self.get_token(force_refresh=True)
                headers["Authorization"] = f"Bearer {self.get_token()}"
                response = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
            response.raise_for_status()
            return response

        return with_retry(_do_request, self.max_retries, self.retry_base_seconds)

    def get_realtime(self, device_id: str, tag_id: str) -> Dict[str, Any]:
        """Read the current value of one tag on one device."""
        url = f"{self.api_prefix}{REALTIME_PATH.format(device_id=device_id)}"
        response = self._authorized_request("POST", url, json={"tagId": tag_id})
        return response.json()

    def get_timeseries(
        self,
        devices: List[Dict[str, str]],
        start_date_time: str,
        end_date_time: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Read historical values for a list of {deviceId, tagTrait} pairs."""
        url = f"{self.api_prefix}{TIMESERIES_PATH}"
        body: Dict[str, Any] = {
            "devices": devices,
            "startDateTime": start_date_time,
            "endDateTime": end_date_time,
        }
        response = self._authorized_request("POST", url, json=body)
        return response.json()

    def get_devices(self, organization_id: str) -> Dict[str, Any]:
        """List device id/name pairs registered under an organization."""
        url = f"{self.api_prefix}{DEVICES_PATH.format(organization_id=organization_id)}"
        response = self._authorized_request("GET", url)
        return response.json()
