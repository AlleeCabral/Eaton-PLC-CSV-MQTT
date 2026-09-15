from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

try:
    from src.modules.cycle_planner import completed_cycle_bounds, cycle_key
    from src.shared.cycle_message import SCHEMA_VERSION, CycleWorkItem
except ModuleNotFoundError:
    from modules.cycle_planner import completed_cycle_bounds, cycle_key
    from shared.cycle_message import SCHEMA_VERSION, CycleWorkItem


def schedule_completed_cycle(
    now_utc: datetime,
    config: Dict[str, Any],
    repo: Any,
    correlation_id: str | None = None,
) -> Dict[str, Any]:
    """Claim and build one work item for the last completed interval."""
    start, end = completed_cycle_bounds(now_utc, config["CYCLE_INTERVAL_MINUTES"])
    key = cycle_key(start)
    correlation_id = correlation_id or str(uuid4())

    claimed = repo.claim_cycle({
        "PartitionKey": key,
        "RowKey": "aggregate",
        "status": "queued",
        "cycleStartUtc": start.isoformat(),
        "cycleEndUtc": end.isoformat(),
        "correlationId": correlation_id,
    })
    if not claimed:
        return {"cycleKey": key, "status": "duplicate", "message": None}

    item = CycleWorkItem(
        schemaVersion=SCHEMA_VERSION,
        cycleKey=key,
        cycleStartUtc=start.isoformat(),
        cycleEndUtc=end.isoformat(),
        correlationId=correlation_id,
    )
    return {"cycleKey": key, "status": "queued", "message": item.to_json()}