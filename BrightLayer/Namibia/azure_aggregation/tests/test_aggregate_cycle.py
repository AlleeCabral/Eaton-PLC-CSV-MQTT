from unittest.mock import MagicMock

from src.modules.aggregate_cycle import AggregateCycle

KPI_MAP = {
    "kpis": [
        {
            "name": "total_flow",
            "operation": "sum",
            "sources": [{"deviceId": "device-1", "traitId": "flow"}],
            "unit": "m3/h",
            "precision": 2,
        }
    ]
}


def test_run_aggregates_snapshots_from_repo():
    repo = MagicMock()
    repo.list_snapshots.return_value = [
        {"deviceId": "device-1", "traitId": "flow", "value": "12.345"},
    ]

    aggregator = AggregateCycle(repo, KPI_MAP, config={})
    result = aggregator.run("2025-07-17T08:00:00Z")

    repo.list_snapshots.assert_called_once_with("2025-07-17T08:00:00Z")
    assert result["status"] == "aggregated"
    assert result["sourceRowCount"] == 1
    assert result["results"]["total_flow"]["value"] == 12.35


def test_run_handles_empty_snapshot_set():
    repo = MagicMock()
    repo.list_snapshots.return_value = []

    aggregator = AggregateCycle(repo, KPI_MAP, config={})
    result = aggregator.run("2025-07-17T08:00:00Z")

    assert result["sourceRowCount"] == 0
    assert result["results"]["total_flow"]["status"] == "no_data"
