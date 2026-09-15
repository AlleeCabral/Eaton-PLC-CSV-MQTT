from datetime import datetime, timezone

import pytest
from azure.core.exceptions import ResourceNotFoundError

from src.modules.cycle_planner import determine_cycle_status
from src.shared.storage_cycle_repo import StorageCycleRepo


class FakeTableClient:
    def __init__(self):
        self.entities = {}

    def upsert_entity(self, entity, mode="merge"):
        key = (entity["PartitionKey"], entity["RowKey"])
        self.entities[key] = dict(entity)

    def create_entity(self, entity):
        key = (entity["PartitionKey"], entity["RowKey"])
        if key in self.entities:
            from azure.core.exceptions import ResourceExistsError

            raise ResourceExistsError("exists")
        self.entities[key] = dict(entity)

    def get_entity(self, partition_key, row_key):
        key = (partition_key, row_key)
        if key not in self.entities:
            raise ResourceNotFoundError("not found")
        return self.entities[key]

    def query_entities(self, query_filter):
        partition_key = query_filter.split("'")[1]
        if " lt " in query_filter:
            return [e for (pk, _rk), e in self.entities.items() if pk < partition_key]
        return [e for (pk, _rk), e in self.entities.items() if pk == partition_key]

    def delete_entity(self, partition_key, row_key):
        self.entities.pop((partition_key, row_key), None)


class FakeTableServiceClient:
    def __init__(self):
        self.created_tables = []
        self._clients = {}

    def create_table_if_not_exists(self, name):
        self.created_tables.append(name)
        self._clients.setdefault(name, FakeTableClient())

    def get_table_client(self, name):
        return self._clients.setdefault(name, FakeTableClient())


CONFIG = {
    "CYCLE_TABLE_STATUS": "CycleStatus",
    "CYCLE_TABLE_SNAPSHOT": "CycleDataSnapshot",
    "CYCLE_TABLE_AUDIT": "CycleAudit",
}


def test_ensure_tables_creates_all_three():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)
    names = repo.ensure_tables()
    assert names == ["CycleStatus", "CycleDataSnapshot", "CycleAudit", "LatestObservation"]
    assert service.created_tables == names


def test_upsert_and_get_status_round_trip():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)

    entity = {
        "PartitionKey": "2025-06-01T10:15:00Z",
        "RowKey": "aggregate",
        "status": "open",
        "expectedCount": 15,
        "receivedCount": 3,
    }
    repo.upsert_status(entity)

    result = repo.get_status("2025-06-01T10:15:00Z")
    assert result["status"] == "open"
    assert result["receivedCount"] == 3


def test_get_status_returns_none_when_missing():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)
    assert repo.get_status("2025-06-01T10:15:00Z") is None


def test_claim_cycle_is_atomic_and_rejects_duplicate():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)
    entity = {
        "PartitionKey": "2025-06-01T10:15:00Z",
        "RowKey": "aggregate",
        "status": "queued",
    }

    assert repo.claim_cycle(entity) is True
    assert repo.claim_cycle(entity) is False
    assert repo.get_status("2025-06-01T10:15:00Z")["status"] == "queued"


def test_upsert_snapshot_writes_to_snapshot_table():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)

    entity = {
        "PartitionKey": "2025-06-01T10:15:00Z",
        "RowKey": "device-1_10549349",
        "value": "1.23",
        "unit": "bar",
        "quality": "online",
    }
    repo.upsert_snapshot(entity)

    snapshot_client = service.get_table_client("CycleDataSnapshot")
    stored = snapshot_client.get_entity("2025-06-01T10:15:00Z", "device-1_10549349")
    assert stored["value"] == "1.23"


def test_list_snapshots_returns_rows_for_cycle_only():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)

    repo.upsert_snapshot({"PartitionKey": "2025-06-01T10:15:00Z", "RowKey": "device-1_a", "value": "1"})
    repo.upsert_snapshot({"PartitionKey": "2025-06-01T10:15:00Z", "RowKey": "device-1_b", "value": "2"})
    repo.upsert_snapshot({"PartitionKey": "2025-06-01T10:20:00Z", "RowKey": "device-1_a", "value": "3"})

    rows = repo.list_snapshots("2025-06-01T10:15:00Z")
    assert len(rows) == 2
    assert {r["value"] for r in rows} == {"1", "2"}


def test_latest_observation_round_trip_and_missing():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)

    assert repo.get_latest_observation("device-1", "flow") is None
    repo.upsert_latest_observation({
        "PartitionKey": "device-1",
        "RowKey": "flow",
        "value": "12.3",
        "lastUpdatedUtc": "2025-06-01T10:00:00Z",
    })

    result = repo.get_latest_observation("device-1", "flow")
    assert result["value"] == "12.3"


def test_audit_round_trip_and_missing():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)

    assert repo.get_audit("2025-06-01T10:15:00Z") is None
    repo.upsert_audit({
        "PartitionKey": "2025-06-01T10:15:00Z",
        "RowKey": "aggregate",
        "mode": "dry_run",
        "candidatePointCount": 12,
    })

    result = repo.get_audit("2025-06-01T10:15:00Z")
    assert result["mode"] == "dry_run"
    assert result["candidatePointCount"] == 12


def test_delete_old_cycles_removes_only_rows_older_than_cutoff():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)

    repo.upsert_status({"PartitionKey": "2025-06-01T00:00:00Z", "RowKey": "aggregate", "status": "sent"})
    repo.upsert_status({"PartitionKey": "2025-06-02T00:00:00Z", "RowKey": "aggregate", "status": "sent"})
    repo.upsert_snapshot({"PartitionKey": "2025-06-01T00:00:00Z", "RowKey": "device-1_a", "value": "1"})
    repo.upsert_snapshot({"PartitionKey": "2025-06-02T00:00:00Z", "RowKey": "device-1_a", "value": "2"})

    deleted = repo.delete_old_cycles("2025-06-01T12:00:00Z")

    assert deleted["CycleStatus"] == 1
    assert deleted["CycleDataSnapshot"] == 1
    assert repo.get_status("2025-06-01T00:00:00Z") is None
    assert repo.get_status("2025-06-02T00:00:00Z") is not None
    assert repo.list_snapshots("2025-06-01T00:00:00Z") == []
    assert repo.list_snapshots("2025-06-02T00:00:00Z") != []


def test_delete_old_cycles_no_op_when_nothing_is_old():
    service = FakeTableServiceClient()
    repo = StorageCycleRepo(service, CONFIG)
    repo.upsert_status({"PartitionKey": "2025-06-02T00:00:00Z", "RowKey": "aggregate", "status": "sent"})

    deleted = repo.delete_old_cycles("2025-06-01T00:00:00Z")

    assert deleted["CycleStatus"] == 0
    assert repo.get_status("2025-06-02T00:00:00Z") is not None


@pytest.mark.parametrize(
    "expected_count,received_count,now_utc,grace_deadline,expected_status",
    [
        (15, 15, datetime(2025, 6, 1, 10, 16, tzinfo=timezone.utc), datetime(2025, 6, 1, 10, 21, 30, tzinfo=timezone.utc), "ready"),
        (15, 20, datetime(2025, 6, 1, 10, 16, tzinfo=timezone.utc), datetime(2025, 6, 1, 10, 21, 30, tzinfo=timezone.utc), "ready"),
        (15, 5, datetime(2025, 6, 1, 10, 16, tzinfo=timezone.utc), datetime(2025, 6, 1, 10, 21, 30, tzinfo=timezone.utc), "open"),
        (15, 5, datetime(2025, 6, 1, 10, 22, tzinfo=timezone.utc), datetime(2025, 6, 1, 10, 21, 30, tzinfo=timezone.utc), "expired"),
        (15, 5, datetime(2025, 6, 1, 10, 21, 30, tzinfo=timezone.utc), datetime(2025, 6, 1, 10, 21, 30, tzinfo=timezone.utc), "expired"),
    ],
)
def test_determine_cycle_status(expected_count, received_count, now_utc, grace_deadline, expected_status):
    assert determine_cycle_status(expected_count, received_count, now_utc, grace_deadline) == expected_status
