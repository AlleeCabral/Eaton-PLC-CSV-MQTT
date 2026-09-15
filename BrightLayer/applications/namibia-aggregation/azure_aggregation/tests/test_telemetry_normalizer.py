from datetime import datetime, timezone

from src.shared.telemetry_normalizer import (
    flatten_brightlayer_timeseries_response,
    normalize_timeseries_records,
)


def test_flatten_picks_most_recent_value_per_series():
    response = {
        "timeSeries": [
            {
                "tagTrait": "10549349",
                "deviceId": "device-1",
                "results": {
                    "values": [
                        {"v": {"unit": "bar", "value": "1.0"}, "dt": "2025-07-17T08:00:00Z"},
                        {"v": {"unit": "bar", "value": "1.5"}, "dt": "2025-07-17T08:05:00Z"},
                    ]
                },
            }
        ]
    }
    flattened = flatten_brightlayer_timeseries_response(response)
    assert len(flattened) == 1
    assert flattened[0]["value"] == "1.5"
    assert flattened[0]["timestampUtc"] == "2025-07-17T08:05:00Z"


def test_flatten_skips_series_with_no_values():
    response = {"timeSeries": [{"tagTrait": "x", "deviceId": "d", "results": {"values": []}}]}
    assert flatten_brightlayer_timeseries_response(response) == []


def test_normalize_marks_recent_value_online():
    now = datetime(2025, 7, 17, 8, 5, 0, tzinfo=timezone.utc)
    records = [{"deviceId": "d1", "traitId": "t1", "value": "1.5", "unit": "bar", "timestampUtc": "2025-07-17T08:04:30Z"}]
    result = normalize_timeseries_records(records, now, stale_timeout_seconds=300, offline_timeout_seconds=600)
    assert result[0]["quality"] == "online"
    assert result[0]["staleSinceUtc"] is None
    assert result[0]["value"] == "1.5"


def test_normalize_marks_aged_value_stale():
    now = datetime(2025, 7, 17, 8, 10, 0, tzinfo=timezone.utc)
    records = [{"deviceId": "d1", "traitId": "t1", "value": "1.5", "unit": "bar", "timestampUtc": "2025-07-17T08:00:00Z"}]
    result = normalize_timeseries_records(records, now, stale_timeout_seconds=300, offline_timeout_seconds=600)
    assert result[0]["quality"] == "stale"
    assert result[0]["staleSinceUtc"] == "2025-07-17T08:00:00Z"


def test_normalize_marks_very_old_value_offline():
    now = datetime(2025, 7, 17, 8, 30, 0, tzinfo=timezone.utc)
    records = [{"deviceId": "d1", "traitId": "t1", "value": "1.5", "unit": "bar", "timestampUtc": "2025-07-17T08:00:00Z"}]
    result = normalize_timeseries_records(records, now, stale_timeout_seconds=300, offline_timeout_seconds=600)
    assert result[0]["quality"] == "offline"


def test_normalize_missing_timestamp_is_offline_not_zero_filled():
    now = datetime(2025, 7, 17, 8, 30, 0, tzinfo=timezone.utc)
    records = [{"deviceId": "d1", "traitId": "t1", "value": None, "unit": "bar", "timestampUtc": None}]
    result = normalize_timeseries_records(records, now, stale_timeout_seconds=300, offline_timeout_seconds=600)
    assert result[0]["quality"] == "offline"
    assert result[0]["value"] is None
