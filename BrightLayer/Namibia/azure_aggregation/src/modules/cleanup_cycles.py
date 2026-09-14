from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict


def run(now_utc: datetime, config: Dict[str, Any], repo: Any) -> Dict[str, Any]:
    """Delete CycleStatus/CycleDataSnapshot rows older than RETENTION_HOURS."""
    cutoff = now_utc - timedelta(hours=config["RETENTION_HOURS"])
    cutoff_iso = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
    deleted_counts = repo.delete_old_cycles(cutoff_iso)
    return {"cutoffUtc": cutoff_iso, "deletedCounts": deleted_counts}
