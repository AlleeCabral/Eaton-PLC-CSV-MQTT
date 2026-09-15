from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Mapping, Optional

try:
    from src.shared.telemetry_normalizer import (
        flatten_brightlayer_timeseries_response,
        normalize_timeseries_records,
    )
except ModuleNotFoundError:
    from shared.telemetry_normalizer import (
        flatten_brightlayer_timeseries_response,
        normalize_timeseries_records,
    )


class FetchSourceTelemetry:
    """Fetches source device telemetry for a cycle window and persists snapshot rows."""

    def __init__(self, brightlayer_client: Any, storage_repo: Any, config: Dict[str, Any]):
        self.brightlayer_client = brightlayer_client
        self.storage_repo = storage_repo
        self.config = config

    def run(
        self,
        cycle_key: str,
        cycle_start_utc: str,
        cycle_end_utc: str,
        devices: List[Dict[str, str]],
        now_utc: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Fetch, normalize, and persist snapshot rows for one cycle.

        `devices` is a list of {"deviceId": ..., "tagTrait": ...} pairs, matching the
        Brightlayer timeseries API request shape.
        """
        overlap_minutes = self.config.get("FETCH_OVERLAP_MINUTES", 15)
        cycle_start = datetime.fromisoformat(cycle_start_utc.replace("Z", "+00:00"))
        fetch_start_utc = (cycle_start - timedelta(minutes=overlap_minutes)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
        response = self.brightlayer_client.get_timeseries(
            devices, fetch_start_utc, cycle_end_utc
        )
        raw_records = flatten_brightlayer_timeseries_response(response)

        for record in raw_records:
            timestamp = record.get("timestampUtc")
            if timestamp and timestamp < cycle_start_utc:
                record["carriedForward"] = True

        observed_keys = {(str(record["deviceId"]), str(record["traitId"])) for record in raw_records}
        for device in devices:
            key = (str(device["deviceId"]), str(device["tagTrait"]))
            if key in observed_keys:
                continue
            latest = self.storage_repo.get_latest_observation(*key)
            if latest is not None:
                raw_records.append({
                    "deviceId": key[0],
                    "traitId": key[1],
                    "value": latest.get("value"),
                    "unit": latest.get("unit"),
                    "timestampUtc": latest.get("lastUpdatedUtc"),
                    "carriedForward": True,
                })

        normalized = normalize_timeseries_records(
            raw_records,
            now_utc or datetime.now(timezone.utc),
            self.config["PLC_STALE_TIMEOUT_SECONDS"],
            self.config["PLC_OFFLINE_TIMEOUT_SECONDS"],
        )

        for record in normalized:
            entity = {
                "PartitionKey": cycle_key,
                "RowKey": f"{record['deviceId']}_{record['traitId']}",
                **record,
            }
            self.storage_repo.upsert_snapshot(entity)
            if not record["carriedForward"]:
                latest = self.storage_repo.get_latest_observation(
                    str(record["deviceId"]), str(record["traitId"])
                )
                previous_timestamp = latest.get("lastUpdatedUtc") if isinstance(latest, Mapping) else None
                if not previous_timestamp or record.get("lastUpdatedUtc", "") > previous_timestamp:
                    self.storage_repo.upsert_latest_observation({
                        "PartitionKey": str(record["deviceId"]),
                        "RowKey": str(record["traitId"]),
                        "value": record.get("value"),
                        "unit": record.get("unit"),
                        "lastUpdatedUtc": record.get("lastUpdatedUtc"),
                    })

        carried_count = sum(1 for record in normalized if record["carriedForward"])
        expected_count = len(devices)
        observed_count = len(observed_keys)
        resolved_count = len(normalized)

        return {
            "cycleKey": cycle_key,
            "cycleStartUtc": cycle_start_utc,
            "cycleEndUtc": cycle_end_utc,
            "expectedPairCount": expected_count,
            "observedPairCount": observed_count,
            "carriedPairCount": carried_count,
            "resolvedPairCount": resolved_count,
            "unresolvedPairCount": max(expected_count - resolved_count, 0),
            "receivedCount": observed_count,
            "status": "fetched",
        }
