from __future__ import annotations

from typing import Any, Dict, List, Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError


class StorageCycleRepo:
    """Table Storage repository for cycle status and telemetry snapshot state."""

    def __init__(self, table_service_client: Any, config: Optional[Dict[str, Any]] = None):
        self.table_service_client = table_service_client
        self.config = config or {}

    def _table_name(self, config_key: str, default: str) -> str:
        return self.config.get(config_key, default)

    def ensure_tables(self) -> List[str]:
        """Create required Azure tables if they do not already exist."""
        table_names = [
            self._table_name("CYCLE_TABLE_STATUS", "CycleStatus"),
            self._table_name("CYCLE_TABLE_SNAPSHOT", "CycleDataSnapshot"),
            self._table_name("CYCLE_TABLE_AUDIT", "CycleAudit"),
            self._table_name("CYCLE_TABLE_LATEST", "LatestObservation"),
        ]
        for name in table_names:
            self.table_service_client.create_table_if_not_exists(name)
        return table_names

    def upsert_status(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Persist (merge) a cycle status row. Entity must include PartitionKey and RowKey."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_STATUS", "CycleStatus")
        )
        table_client.upsert_entity(entity, mode="merge")
        return entity

    def claim_cycle(self, entity: Dict[str, Any]) -> bool:
        """Atomically create a cycle row, returning False when it already exists."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_STATUS", "CycleStatus")
        )
        try:
            table_client.create_entity(entity)
        except ResourceExistsError:
            return False
        return True

    def get_status(self, cycle_start_key: str, row_key: str = "aggregate") -> Optional[Dict[str, Any]]:
        """Read back the status row for a cycle, or None if it doesn't exist."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_STATUS", "CycleStatus")
        )
        try:
            return table_client.get_entity(partition_key=cycle_start_key, row_key=row_key)
        except ResourceNotFoundError:
            return None

    def upsert_snapshot(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Persist (merge) a telemetry snapshot row. Entity must include PartitionKey and RowKey."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_SNAPSHOT", "CycleDataSnapshot")
        )
        table_client.upsert_entity(entity, mode="merge")
        return entity

    def list_snapshots(self, cycle_key: str) -> List[Dict[str, Any]]:
        """Return all snapshot rows persisted for a given cycle."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_SNAPSHOT", "CycleDataSnapshot")
        )
        entities = table_client.query_entities(query_filter=f"PartitionKey eq '{cycle_key}'")
        return list(entities)

    def upsert_latest_observation(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Persist the latest known observation for one configured source pair."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_LATEST", "LatestObservation")
        )
        table_client.upsert_entity(entity, mode="replace")
        return entity

    def get_latest_observation(self, device_id: str, trait_id: str) -> Optional[Dict[str, Any]]:
        """Return the latest known observation for a source pair, if available."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_LATEST", "LatestObservation")
        )
        try:
            return table_client.get_entity(partition_key=device_id, row_key=trait_id)
        except ResourceNotFoundError:
            return None

    def upsert_audit(self, entity: Dict[str, Any]) -> Dict[str, Any]:
        """Persist an audit record for a cycle result."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_AUDIT", "CycleAudit")
        )
        table_client.upsert_entity(entity, mode="replace")
        return entity

    def get_audit(self, cycle_key: str, row_key: str = "aggregate") -> Optional[Dict[str, Any]]:
        """Read a cycle audit record, or None when it does not exist."""
        table_client = self.table_service_client.get_table_client(
            self._table_name("CYCLE_TABLE_AUDIT", "CycleAudit")
        )
        try:
            return table_client.get_entity(partition_key=cycle_key, row_key=row_key)
        except ResourceNotFoundError:
            return None

    def delete_old_cycles(self, cutoff_iso: str) -> Dict[str, int]:
        """Delete CycleStatus and CycleDataSnapshot rows for cycles older than the cutoff.

        Cycle keys are ISO-8601 strings (e.g. "2025-06-01T10:15:00Z"), which sort
        lexically the same as chronologically, so a plain string comparison filter is safe.
        """
        deleted_counts: Dict[str, int] = {}
        for config_key, default_name in (
            ("CYCLE_TABLE_STATUS", "CycleStatus"),
            ("CYCLE_TABLE_SNAPSHOT", "CycleDataSnapshot"),
        ):
            table_name = self._table_name(config_key, default_name)
            table_client = self.table_service_client.get_table_client(table_name)
            old_entities = list(table_client.query_entities(query_filter=f"PartitionKey lt '{cutoff_iso}'"))
            for entity in old_entities:
                table_client.delete_entity(entity["PartitionKey"], entity["RowKey"])
            deleted_counts[table_name] = len(old_entities)
        return deleted_counts
