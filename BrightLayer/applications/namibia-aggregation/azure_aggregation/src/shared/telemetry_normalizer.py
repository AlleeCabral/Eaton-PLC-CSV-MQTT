from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


def _parse_utc(timestamp: Optional[str]) -> Optional[datetime]:
    """Parse an ISO-8601 UTC timestamp (Brightlayer uses a trailing 'Z'). Returns None if unparseable."""
    if not timestamp:
        return None
    normalized = timestamp[:-1] + "+00:00" if timestamp.endswith("Z") else timestamp
    try:
        return datetime.fromisoformat(normalized).astimezone(timezone.utc)
    except ValueError:
        return None


def flatten_brightlayer_timeseries_response(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten a raw /dashboard/devices/timeseries response into one record per
    device/trait, keeping only the most recent value in each series."""
    flattened: List[Dict[str, Any]] = []
    for series in response.get("timeSeries", []) or []:
        values = ((series.get("results") or {}).get("values")) or []
        if not values:
            continue
        latest = max(values, key=lambda v: v.get("dt") or "")
        point = latest.get("v") or {}
        flattened.append({
            "deviceId": series.get("deviceId"),
            "traitId": series.get("tagTrait"),
            "value": point.get("value"),
            "unit": point.get("unit"),
            "timestampUtc": latest.get("dt"),
        })
    return flattened


def normalize_timeseries_records(
    records: Iterable[Dict[str, Any]],
    now_utc: datetime,
    stale_timeout_seconds: int,
    offline_timeout_seconds: int,
) -> List[Dict[str, Any]]:
    """Normalize source records into snapshot rows with explicit freshness metadata.

    Per the operational rules for unstable PLC connectivity (see iteration_memory.md):
    a value that hasn't refreshed is tagged stale/offline and its last known value is
    carried forward — it is never zero-filled or silently treated as fresh.
    """
    normalized: List[Dict[str, Any]] = []
    for record in records:
        last_updated = _parse_utc(record.get("timestampUtc"))
        if last_updated is None:
            quality = "offline"
        else:
            age_seconds = (now_utc - last_updated).total_seconds()
            if age_seconds <= stale_timeout_seconds:
                quality = "online"
            elif age_seconds <= offline_timeout_seconds:
                quality = "stale"
            else:
                quality = "offline"

        normalized.append({
            "deviceId": record.get("deviceId"),
            "traitId": record.get("traitId"),
            "value": record.get("value"),
            "unit": record.get("unit"),
            "lastUpdatedUtc": record.get("timestampUtc"),
            "staleSinceUtc": record.get("timestampUtc") if quality != "online" else None,
            "quality": quality,
            "carriedForward": bool(record.get("carriedForward", False)),
        })
    return normalized
