from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Dict, Iterable, Mapping

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.brightlayer_client import BrightlayerClient


DEVICE_REGISTRY_PATH = PROJECT_ROOT / "config" / "brightlayer-test-devices.json"


def _load_test_device_registry(path: Path = DEVICE_REGISTRY_PATH) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        registry = json.load(handle)
    organization = registry["organizations"][0]
    device = organization["devices"][0]
    return {
        "apiPrefix": registry["apiPrefix"],
        "serviceAccountId": registry["serviceAccountId"],
        "organizationId": organization["organizationId"],
        "organizationCode": organization.get("organizationCode"),
        "gatewayId": device["gatewayId"],
        "gatewayName": device["gatewayName"],
        "childDeviceName": device["childDeviceName"],
        "childDeviceId": device["childDeviceId"],
        "ontologyProfileId": device["ontologyProfileId"],
        "adopterId": device["adopterId"],
        "traitIds": [trait["tagId"] for trait in device["traits"]],
    }


TEST_DEVICE = _load_test_device_registry()
API_PREFIX = os.getenv("BRIGHTLAYER_API_PREFIX", TEST_DEVICE["apiPrefix"])
ORGANIZATION_ID = os.getenv("BRIGHTLAYER_ORGANIZATION_ID", TEST_DEVICE["organizationId"])
PARENT_DEVICE_ID = TEST_DEVICE["gatewayId"]
PARENT_DEVICE_NAME = TEST_DEVICE["gatewayName"]
CHILD_DEVICE_NAME = TEST_DEVICE["childDeviceName"]
LOOKBACK_HOURS = int(os.getenv("BRIGHTLAYER_LOOKBACK_HOURS", "24"))
QUICK_LOOKBACK_MINUTES = int(os.getenv("BRIGHTLAYER_PROBE_QUICK_LOOKBACK_MINUTES", "15"))


def _format_api_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _registry_probe_inputs(
    device: Mapping[str, Any],
    quick_mode: bool,
    end: datetime | None = None,
) -> tuple[str, list[str], str, str]:
    end = end or datetime.now(timezone.utc)
    start = (
        end - timedelta(minutes=QUICK_LOOKBACK_MINUTES)
        if quick_mode
        else end - timedelta(hours=LOOKBACK_HOURS)
    )
    trait_ids = device["traitIds"][:1] if quick_mode else device["traitIds"]
    return device["childDeviceId"], trait_ids, _format_api_utc(start), _format_api_utc(end)


def _targeted_probe_inputs(environment: Mapping[str, str]) -> tuple[str, list[str], str, str] | None:
    device_id = environment.get("BRIGHTLAYER_PROBE_DEVICE_ID")
    trait_ids = [
        value.strip()
        for value in environment.get("BRIGHTLAYER_PROBE_TRAIT_IDS", "").split(",")
        if value.strip()
    ]
    start_utc = environment.get("BRIGHTLAYER_PROBE_START_UTC")
    end_utc = environment.get("BRIGHTLAYER_PROBE_END_UTC")
    supplied = (device_id, trait_ids, start_utc, end_utc)
    if not any(supplied):
        return None
    if not device_id or not trait_ids or not start_utc or not end_utc:
        raise RuntimeError(
            "Set BRIGHTLAYER_PROBE_DEVICE_ID, BRIGHTLAYER_PROBE_TRAIT_IDS, "
            "BRIGHTLAYER_PROBE_START_UTC, and BRIGHTLAYER_PROBE_END_UTC together"
        )
    for name, value in (
        ("BRIGHTLAYER_PROBE_START_UTC", start_utc),
        ("BRIGHTLAYER_PROBE_END_UTC", end_utc),
    ):
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError as exc:
            raise RuntimeError(f"{name} must use YYYY-MM-DDTHH:MM:SSZ") from exc
    return device_id, trait_ids, start_utc, end_utc


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Set {name} in the current process before running this read-only probe")
    return value


def _walk(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _matching_objects(payload: Any) -> list[Dict[str, Any]]:
    names = {PARENT_DEVICE_NAME.lower(), CHILD_DEVICE_NAME.lower()}
    matches = []
    for item in _walk(payload):
        item_name = str(item.get("name") or item.get("displayName") or "").lower()
        if item_name in names:
            matches.append({
                key: item.get(key)
                for key in ("id", "deviceId", "name", "displayName", "parentId", "children")
                if key in item
            })
    return matches


def _get_timeseries(
    client: BrightlayerClient,
    pairs: list[Dict[str, str]],
    start_utc: str,
    end_utc: str,
) -> Dict[str, Any]:
    return client.get_timeseries(pairs, start_utc, end_utc)


def _run_stage(report: Dict[str, Any], name: str, operation: Callable[[], Any]) -> Any:
    started = perf_counter()
    try:
        result = operation()
    except requests.HTTPError as exc:
        response = exc.response
        failure = {
            "ok": False,
            "statusCode": response.status_code if response is not None else None,
            "contentType": response.headers.get("content-type") if response is not None else None,
        }
        if response is not None and "application/json" in (response.headers.get("content-type") or ""):
            try:
                body = response.json()
                failure["message"] = body.get("message")
                failure["isError"] = body.get("isError")
            except (ValueError, AttributeError):
                pass
        report[name] = failure
        return None
    report[name] = {
        "ok": True,
        "latencyMs": round((perf_counter() - started) * 1000, 1),
    }
    return result


def main() -> None:
    quick_mode = os.getenv("BRIGHTLAYER_PROBE_QUICK", "").lower() in {"1", "true", "yes"}
    client = BrightlayerClient(
        api_prefix=API_PREFIX,
        service_account_id=_required_env("BRIGHTLAYER_SERVICE_ACCOUNT_ID"),
        service_account_secret=_required_env("BRIGHTLAYER_SERVICE_ACCOUNT_SECRET"),
        max_retries=1,
        retry_base_seconds=0,
    )
    report: Dict[str, Any] = {
        "apiPrefix": API_PREFIX,
        "organizationId": ORGANIZATION_ID,
        "organizationCode": TEST_DEVICE["organizationCode"],
        "configuredDevice": {
            "gatewayId": TEST_DEVICE["gatewayId"],
            "gatewayName": TEST_DEVICE["gatewayName"],
            "childDeviceId": TEST_DEVICE["childDeviceId"],
            "childDeviceName": TEST_DEVICE["childDeviceName"],
            "ontologyProfileId": TEST_DEVICE["ontologyProfileId"],
            "adopterId": TEST_DEVICE["adopterId"],
        },
        "writeOperationsAttempted": 0,
    }

    client.get_token()
    report["tokenGenerated"] = True

    if quick_mode:
        report["deviceDiscovery"] = {"skipped": True, "reason": "quick-mode"}
        report["matchingDeviceObjects"] = []
    else:
        devices = _run_stage(report, "deviceDiscovery", lambda: client.get_devices(ORGANIZATION_ID))
        report["matchingDeviceObjects"] = _matching_objects(devices) if devices is not None else []

    targeted_inputs = _targeted_probe_inputs(os.environ)
    if targeted_inputs:
        device_id, trait_ids, start_utc, end_utc = targeted_inputs
        pairs = [{"deviceId": device_id, "tagTrait": trait_id} for trait_id in trait_ids]
        report["probeMode"] = "targeted"
    else:
        device_id, trait_ids, start_utc, end_utc = _registry_probe_inputs(
            TEST_DEVICE, quick_mode
        )
        pairs = [{"deviceId": device_id, "tagTrait": trait_id} for trait_id in trait_ids]
        report["probeMode"] = "registry-quick" if quick_mode else "registry-default"

    report["probeDeviceId"] = device_id
    report["probeTraitIds"] = trait_ids
    report["realtimeProbes"] = {"skipped": True, "reason": "traits-use-timeseries"}

    timeseries = _run_stage(
        report,
        "timeseriesStage",
        lambda: _get_timeseries(client, pairs, start_utc, end_utc),
    )
    report["requestedPairCount"] = len(pairs)
    report["timeseriesWindowUtc"] = {"start": start_utc, "end": end_utc}
    report["returnedSeriesCount"] = len(timeseries.get("timeSeries", []) or []) if timeseries else 0
    report["timeseriesResponse"] = timeseries

    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()