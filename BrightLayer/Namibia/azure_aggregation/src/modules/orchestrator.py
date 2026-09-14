from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

try:
    from src.modules.cycle_planner import cycle_bounds, cycle_key as compute_cycle_key, determine_cycle_status
except ModuleNotFoundError:
    from modules.cycle_planner import cycle_bounds, cycle_key as compute_cycle_key, determine_cycle_status

ACTIVE_STATUSES = {"open", "ready", "processing"}


def plan_cycle(now_utc: datetime, config: Dict[str, Any], repo: Any) -> Dict[str, Any]:
    """Create or refresh the CycleStatus row for the cycle containing `now_utc`."""
    cycle_start, cycle_end, grace_deadline = cycle_bounds(now_utc, config["CYCLE_GRACE_SECONDS"])
    key = compute_cycle_key(now_utc)

    existing = repo.get_status(key)
    received_count = existing.get("receivedCount", 0) if existing else 0
    expected_count = config["EXPECTED_PLC_COUNT"]

    # A cycle that already reached a terminal state must not be recomputed as open/ready again.
    if existing and existing.get("status") in ("sent", "failed", "expired"):
        status = existing["status"]
    else:
        status = determine_cycle_status(expected_count, received_count, now_utc, grace_deadline)

    repo.upsert_status({
        "PartitionKey": key,
        "RowKey": "aggregate",
        "status": status,
        "expectedCount": expected_count,
        "receivedCount": received_count,
        "cycleStartUtc": cycle_start.isoformat(),
        "cycleEndUtc": cycle_end.isoformat(),
        "graceDeadlineUtc": grace_deadline.isoformat(),
    })

    return {
        "cycleKey": key,
        "cycleStartUtc": cycle_start.isoformat(),
        "cycleEndUtc": cycle_end.isoformat(),
        "graceDeadlineUtc": grace_deadline.isoformat(),
        "status": status,
        "expectedCount": expected_count,
        "receivedCount": received_count,
    }


def run_cycle_pipeline(
    cycle_plan: Dict[str, Any],
    fetch_source_telemetry: Any,
    aggregate_cycle: Any,
    writeback: Any,
    repo: Any,
    devices: List[Dict[str, str]],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Fetch telemetry for the cycle; aggregate and publish only once it's ready.

    Aggregate/writeback failures are caught here (not propagated): the cycle is
    kept `open` for retry on the next tick while `retryCount < MAX_RETRIES`, and
    only marked `failed` (terminal) once the limit is reached. Callers are still
    expected to skip invoking this at all for cycles already in a terminal state
    (sent/failed/expired) — see function_app.py's guard.
    """
    cycle_key = cycle_plan["cycleKey"]

    fetch_result = fetch_source_telemetry.run(
        cycle_key, cycle_plan["cycleStartUtc"], cycle_plan["cycleEndUtc"], devices
    )
    received_count = fetch_result["receivedCount"]

    grace_deadline = datetime.fromisoformat(cycle_plan["graceDeadlineUtc"])
    now_utc = datetime.now(timezone.utc)
    status = determine_cycle_status(cycle_plan["expectedCount"], received_count, now_utc, grace_deadline)

    repo.upsert_status({
        "PartitionKey": cycle_key,
        "RowKey": "aggregate",
        "status": "processing" if status == "ready" else status,
        "receivedCount": received_count,
    })

    result: Dict[str, Any] = {"cycleKey": cycle_key, "fetch": fetch_result, "status": status}

    if status != "ready":
        return result

    try:
        aggregate_result = aggregate_cycle.run(cycle_key)
        writeback_result = writeback.run(cycle_key, aggregate_result["results"])
        if writeback_result["status"] not in ("sent", "skipped"):
            raise RuntimeError(f"writeback returned unexpected status: {writeback_result['status']}")
    except Exception as exc:
        existing = repo.get_status(cycle_key) or {}
        retry_count = existing.get("retryCount", 0) + 1
        max_retries = config.get("MAX_RETRIES", 3)
        final_status = "failed" if retry_count >= max_retries else "open"
        repo.upsert_status({
            "PartitionKey": cycle_key,
            "RowKey": "aggregate",
            "status": final_status,
            "retryCount": retry_count,
            "lastError": str(exc)[:500],
        })
        result["status"] = final_status
        result["error"] = str(exc)
        result["retryCount"] = retry_count
        return result

    repo.upsert_status({
        "PartitionKey": cycle_key,
        "RowKey": "aggregate",
        "status": "sent",
        "retryCount": 0,
        "lastError": "",
    })

    result["aggregate"] = aggregate_result
    result["writeback"] = writeback_result
    result["status"] = "sent"
    return result
