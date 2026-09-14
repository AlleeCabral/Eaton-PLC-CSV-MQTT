from __future__ import annotations

import json
from typing import Any, Dict

try:
    from src.shared.cycle_message import CycleWorkItem
except ModuleNotFoundError:
    from shared.cycle_message import CycleWorkItem


class IncompleteCycleError(RuntimeError):
    """Raised so Queue Storage retries a cycle that cannot yet be completed."""


def build_dry_run_candidates(aggregates: Dict[str, Dict[str, Any]]) -> list[Dict[str, Any]]:
    """Build values that can be mapped to destination channel IDs once available."""
    fields = (
        "value",
        "unit",
        "status",
        "expectedSourceCount",
        "sourceCount",
        "freshSourceCount",
        "staleSourceCount",
        "offlineSourceCount",
        "carriedSourceCount",
    )
    return [
        {"name": name, **{field: result.get(field, 0) for field in fields}}
        for name, result in aggregates.items()
    ]


def process_cycle_work_item(
    item: CycleWorkItem,
    context: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """Fetch, validate, aggregate, and publish one idempotent queued cycle."""
    repo = context["repo"]
    existing = repo.get_status(item.cycleKey) or {}
    if existing.get("status") in {"sent", "dry_run_completed"}:
        return {"cycleKey": item.cycleKey, "status": "duplicate"}

    fetch_result = context["fetch_source_telemetry"].run(
        item.cycleKey,
        item.cycleStartUtc,
        item.cycleEndUtc,
        context["devices"],
    )
    expected = fetch_result["expectedPairCount"]
    observed = fetch_result["observedPairCount"]
    resolved = fetch_result["resolvedPairCount"]
    strict = config["AGGREGATION_MODE"] == "strict"
    complete = expected > 0 and resolved == expected and (not strict or observed == expected)

    coverage = {
        "expectedPairCount": expected,
        "observedPairCount": observed,
        "carriedPairCount": fetch_result["carriedPairCount"],
        "resolvedPairCount": resolved,
        "unresolvedPairCount": fetch_result["unresolvedPairCount"],
    }
    if not complete:
        repo.upsert_status({
            "PartitionKey": item.cycleKey,
            "RowKey": "aggregate",
            "status": "incomplete",
            **coverage,
        })
        raise IncompleteCycleError(
            f"Cycle {item.cycleKey} is incomplete: resolved {resolved}/{expected}, observed {observed}/{expected}"
        )

    repo.upsert_status({
        "PartitionKey": item.cycleKey,
        "RowKey": "aggregate",
        "status": "processing",
        **coverage,
    })
    aggregate_result = context["aggregate_cycle"].run(item.cycleKey)
    if config["WRITEBACK_MODE"] == "dry_run":
        candidates = build_dry_run_candidates(aggregate_result["results"])
        repo.upsert_audit({
            "PartitionKey": item.cycleKey,
            "RowKey": "aggregate",
            "mode": "dry_run",
            "correlationId": item.correlationId,
            "cycleStartUtc": item.cycleStartUtc,
            "cycleEndUtc": item.cycleEndUtc,
            "coverageJson": json.dumps(coverage, separators=(",", ":"), sort_keys=True),
            "aggregatesJson": json.dumps(aggregate_result["results"], separators=(",", ":"), sort_keys=True),
            "candidatePayloadJson": json.dumps({"trends": candidates}, separators=(",", ":"), sort_keys=True),
            "candidatePointCount": len(candidates),
        })
        repo.upsert_status({
            "PartitionKey": item.cycleKey,
            "RowKey": "aggregate",
            "status": "dry_run_completed",
            "candidatePointCount": len(candidates),
            **coverage,
        })
        return {
            "cycleKey": item.cycleKey,
            "status": "dry_run_completed",
            "coverage": coverage,
            "aggregate": aggregate_result,
            "candidatePayload": {"trends": candidates},
        }

    writeback_result = context["writeback"].run(item.cycleKey, aggregate_result["results"])
    if writeback_result.get("status") != "sent":
        raise IncompleteCycleError(
            f"Cycle {item.cycleKey} produced no publishable aggregate payload"
        )

    repo.upsert_status({
        "PartitionKey": item.cycleKey,
        "RowKey": "aggregate",
        "status": "sent",
        "publishedPointCount": writeback_result["pointCount"],
        **coverage,
    })
    return {
        "cycleKey": item.cycleKey,
        "status": "sent",
        "coverage": coverage,
        "aggregate": aggregate_result,
        "writeback": writeback_result,
    }