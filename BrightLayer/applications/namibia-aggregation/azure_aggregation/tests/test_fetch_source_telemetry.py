from datetime import datetime, timezone
from unittest.mock import MagicMock

from src.modules.fetch_source_telemetry import FetchSourceTelemetry

CONFIG = {
    "FETCH_OVERLAP_MINUTES": 15,
    "PLC_STALE_TIMEOUT_SECONDS": 300,
    "PLC_OFFLINE_TIMEOUT_SECONDS": 600,
}


def test_run_fetches_normalizes_and_persists_snapshots():
    brightlayer_client = MagicMock()
    brightlayer_client.get_timeseries.return_value = {
        "timeSeries": [
            {
                "tagTrait": "10549349",
                "deviceId": "device-1",
                "results": {"values": [{"v": {"unit": "bar", "value": "1.5"}, "dt": "2025-07-17T08:05:00Z"}]},
            },
            {
                "tagTrait": "10549345",
                "deviceId": "device-1",
                "results": {"values": [{"v": {"unit": "uS/cm", "value": "220"}, "dt": "2025-07-17T08:04:50Z"}]},
            },
        ]
    }

    storage_repo = MagicMock()

    fetcher = FetchSourceTelemetry(brightlayer_client, storage_repo, CONFIG)
    devices = [
        {"deviceId": "device-1", "tagTrait": "10549349"},
        {"deviceId": "device-1", "tagTrait": "10549345"},
    ]

    result = fetcher.run("2025-07-17T08:05:00Z", "2025-07-17T08:00:00Z", "2025-07-17T08:05:00Z", devices)

    brightlayer_client.get_timeseries.assert_called_once_with(
        devices, "2025-07-17T07:45:00Z", "2025-07-17T08:05:00Z"
    )
    assert result["receivedCount"] == 2
    assert result["observedPairCount"] == 2
    assert result["carriedPairCount"] == 0
    assert result["unresolvedPairCount"] == 0
    assert result["status"] == "fetched"
    assert storage_repo.upsert_snapshot.call_count == 2
    assert storage_repo.upsert_latest_observation.call_count == 2

    first_entity = storage_repo.upsert_snapshot.call_args_list[0].args[0]
    assert first_entity["PartitionKey"] == "2025-07-17T08:05:00Z"
    assert first_entity["RowKey"] == "device-1_10549349"
    assert first_entity["value"] == "1.5"


def test_run_returns_zero_received_count_when_no_series():
    brightlayer_client = MagicMock()
    brightlayer_client.get_timeseries.return_value = {"timeSeries": []}
    storage_repo = MagicMock()
    storage_repo.get_latest_observation.return_value = None

    fetcher = FetchSourceTelemetry(brightlayer_client, storage_repo, CONFIG)
    result = fetcher.run("2025-07-17T08:05:00Z", "2025-07-17T08:00:00Z", "2025-07-17T08:05:00Z", [])

    assert result["receivedCount"] == 0
    assert result["unresolvedPairCount"] == 0
    storage_repo.upsert_snapshot.assert_not_called()


def test_run_fetches_all_pairs_together_and_carries_missing_latest_value():
    brightlayer_client = MagicMock()
    brightlayer_client.get_timeseries.return_value = {
        "timeSeries": [{
            "tagTrait": "today",
            "deviceId": "device-1",
            "results": {"values": [{"v": {"unit": "kWh", "value": "10"}, "dt": "2025-07-17T08:05:00Z"}]},
        }]
    }
    storage_repo = MagicMock()
    storage_repo.get_latest_observation.return_value = {
        "value": "7",
        "unit": "kWh",
        "lastUpdatedUtc": "2025-07-17T08:00:00Z",
    }
    fetcher = FetchSourceTelemetry(brightlayer_client, storage_repo, CONFIG)
    devices = [
        {"deviceId": "device-1", "tagTrait": "today"},
        {"deviceId": "device-2", "tagTrait": "today"},
    ]

    result = fetcher.run(
        "2025-07-17T08:05:00Z",
        "2025-07-17T08:00:00Z",
        "2025-07-17T08:05:00Z",
        devices,
        now_utc=datetime(2025, 7, 17, 8, 6, tzinfo=timezone.utc),
    )

    brightlayer_client.get_timeseries.assert_called_once_with(
        devices, "2025-07-17T07:45:00Z", "2025-07-17T08:05:00Z"
    )
    assert result["expectedPairCount"] == 2
    assert result["observedPairCount"] == 1
    assert result["carriedPairCount"] == 1
    assert result["resolvedPairCount"] == 2
    carried = storage_repo.upsert_snapshot.call_args_list[1].args[0]
    assert carried["deviceId"] == "device-2"
    assert carried["value"] == "7"
    assert carried["carriedForward"] is True
    assert carried["quality"] == "stale"
