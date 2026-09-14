from __future__ import annotations

from typing import Any, Dict

try:
    from src.shared.aggregations import aggregate_kpis
except ModuleNotFoundError:
    from shared.aggregations import aggregate_kpis


class AggregateCycle:
    """Reads snapshot rows for a cycle and computes configured KPI aggregates."""

    def __init__(self, repo: Any, kpi_map: Dict[str, Any], config: Dict[str, Any]):
        self.repo = repo
        self.kpi_map = kpi_map
        self.config = config

    def run(self, cycle_key: str) -> Dict[str, Any]:
        """Aggregate all configured KPIs for a cycle from its persisted snapshot rows."""
        snapshot_rows = self.repo.list_snapshots(cycle_key)
        results = aggregate_kpis(snapshot_rows, self.kpi_map)
        return {
            "cycleKey": cycle_key,
            "status": "aggregated",
            "sourceRowCount": len(snapshot_rows),
            "results": results,
        }
